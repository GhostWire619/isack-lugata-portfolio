// Fullscreen, scroll-driven 3D photo gallery. Loaded only when the gallery opens.
// Every scroll-driven value is a pure function of scroll position, so scrubbing
// backwards plays each transition in reverse.
import * as THREE from './three.module.min.js';

const STYLESHEET = '/assets/personal/castle/castle-gallery.css';
const BIWA = '/assets/personal/castle/nakime-biwa.m4a';
const PAGE_SLEEP = '/assets/personal/zenitsu/die.webp';
const SPRITES = {
  idle: { src: '/assets/personal/castle/zenitsu/idle.webp', lite: '/assets/personal/castle/zenitsu-lite/idle.webp', frames: 19, cols: 4, rows: 5 },
  run: { src: '/assets/personal/castle/zenitsu/run.webp', lite: '/assets/personal/castle/zenitsu-lite/run.webp', frames: 9, cols: 3, rows: 3 },
  slash: { src: '/assets/personal/castle/zenitsu/atk01.webp', lite: '/assets/personal/castle/zenitsu-lite/atk01.webp', frames: 19, cols: 4, rows: 5 },
  spin: { src: '/assets/personal/castle/zenitsu/skl01.webp', lite: '/assets/personal/castle/zenitsu-lite/skl01.webp', frames: 21, cols: 4, rows: 6 },
  dash: { src: '/assets/personal/castle/zenitsu/skl02.webp', lite: '/assets/personal/castle/zenitsu-lite/skl02.webp', frames: 36, cols: 5, rows: 8 },
  hit: { src: '/assets/personal/castle/zenitsu/hit01.webp', lite: '/assets/personal/castle/zenitsu-lite/hit01.webp', frames: 7, cols: 2, rows: 4 },
  faint: { src: '/assets/personal/castle/zenitsu/die.webp', lite: '/assets/personal/castle/zenitsu-lite/die.webp', frames: 23, cols: 4, rows: 6 },
};
const ROOM_NUMERALS = ['壱', '弐', '参', '肆', '伍', '陸', '漆', '捌'];
const PHOTOS_PER_ROOM = 3;
const HALL = { w: 17, d: 13, h: 9.4 };
const INTRO_SECONDS = 6.4;
const CUT_AT = 1;
const MAX_ACCENTS = 3;
const ACCENT_GAP_MS = 20000;

// Phones and small devices get a separate, much cheaper render path.
function detectLite() {
  const small = Math.min(innerWidth, innerHeight) < 700;
  const coarse = matchMedia('(pointer: coarse)').matches;
  const lowMemory = navigator.deviceMemory !== undefined && navigator.deviceMemory <= 4;
  return small || coarse || lowMemory;
}
let textureAnisotropy = 8;

const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const smooth = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * (3 - 2 * t); };
const smoother = (a, b, v) => { const t = clamp((v - a) / (b - a)); return t * t * t * (t * (6 * t - 15) + 10); };
const lerp = (a, b, t) => a + (b - a) * t;
const v3 = (x = 0, y = 0, z = 0) => new THREE.Vector3(x, y, z);

// Deterministic randomness keeps the castle identical between visits.
function makeRandom(seed) {
  let s = seed >>> 0;
  return (a = 0, b = 1) => {
    s = (s + 0x6D2B79F5) >>> 0;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return a + (((t ^ (t >>> 14)) >>> 0) / 4294967296) * (b - a);
  };
}

/* ---------- procedural textures ---------- */

function canvasTexture(width, height, paint, { repeat = false, color = true } = {}) {
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height;
  paint(canvas.getContext('2d'), width, height);
  const texture = new THREE.CanvasTexture(canvas);
  if (color) texture.colorSpace = THREE.SRGBColorSpace;
  if (repeat) texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.anisotropy = textureAnisotropy;
  return texture;
}

function paintWood(ctx, w, h, base = [58, 30, 17]) {
  const rand = makeRandom(11);
  ctx.fillStyle = `rgb(${base})`;
  ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 1500; i++) {
    const y = rand(0, h), light = rand() > .55;
    ctx.strokeStyle = light ? `rgba(150,92,52,${rand(.03, .13)})` : `rgba(14,6,3,${rand(.05, .24)})`;
    ctx.lineWidth = rand(.4, 2.6);
    ctx.beginPath();
    ctx.moveTo(0, y);
    const wobble = rand(-7, 7);
    ctx.bezierCurveTo(w * .3, y + wobble, w * .7, y - wobble, w, y);
    ctx.stroke();
  }
  for (let i = 0; i < 9; i++) {
    const x = rand(0, w), y = rand(0, h), rx = rand(16, 48), ry = rand(4, 11);
    for (let ring = 5; ring > 0; ring--) {
      ctx.strokeStyle = `rgba(16,7,3,${.1 + ring * .03})`;
      ctx.lineWidth = 1.1;
      ctx.beginPath();
      ctx.ellipse(x, y, rx * ring / 5, ry * ring / 5, 0, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
}

function paintShoji(ctx, w, h) {
  const rand = makeRandom(23);
  const glow = ctx.createRadialGradient(w / 2, h * .42, 20, w / 2, h * .42, h * .68);
  glow.addColorStop(0, '#ffe2ab');
  glow.addColorStop(.55, '#f4a964');
  glow.addColorStop(1, '#a9542a');
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, w, h);
  for (let i = 0; i < 1100; i++) {
    ctx.strokeStyle = `rgba(255,244,214,${rand(.02, .1)})`;
    ctx.lineWidth = rand(.3, 1);
    const x = rand(0, w), y = rand(0, h), a = rand(0, 6.3), l = rand(6, 34);
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l);
    ctx.stroke();
  }
  const panelTop = h * .8;
  ctx.fillStyle = '#21100a';
  ctx.fillRect(0, panelTop, w, h - panelTop);
  ctx.fillStyle = '#17090530';
  for (let i = 0; i < 26; i++) ctx.fillRect(0, panelTop + i * (h - panelTop) / 26, w, 1);
  ctx.fillStyle = '#1b0d07';
  const columns = 4, rows = 7;
  for (let i = 1; i < columns; i++) ctx.fillRect(i * w / columns - 3, 0, 6, panelTop);
  for (let i = 1; i < rows; i++) ctx.fillRect(0, i * panelTop / rows - 3, w, 6);
  ctx.lineWidth = 22;
  ctx.strokeStyle = '#150a05';
  ctx.strokeRect(11, 11, w - 22, h - 22);
  ctx.fillRect(0, panelTop - 6, w, 12);
}

function paintTatami(ctx, w, h) {
  const rand = makeRandom(5);
  ctx.fillStyle = '#6d6330';
  ctx.fillRect(0, 0, w, h);
  for (let y = 0; y < h; y += 3) {
    ctx.fillStyle = `rgba(${rand() > .5 ? '150,136,70' : '40,34,14'},${rand(.1, .32)})`;
    ctx.fillRect(0, y, w, 1.6);
  }
  ctx.fillStyle = '#231108';
  ctx.fillRect(0, 0, w, 22);
  ctx.fillRect(0, h - 22, w, 22);
  ctx.fillStyle = '#b57f3c';
  for (let x = 12; x < w; x += 28) { ctx.fillRect(x, 8, 12, 5); ctx.fillRect(x, h - 13, 12, 5); }
}

function paintGlow(ctx, w, h) {
  const g = ctx.createRadialGradient(w / 2, h / 2, 0, w / 2, h / 2, w / 2);
  g.addColorStop(0, 'rgba(255,255,255,1)');
  g.addColorStop(.25, 'rgba(255,255,255,.5)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);
}

/* ---------- shaders ---------- */

const NOISE_GLSL = /* glsl */`
  float hash(vec2 p){ p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
  float noise(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f);
    return mix(mix(hash(i), hash(i+vec2(1,0)), f.x), mix(hash(i+vec2(0,1)), hash(i+vec2(1,1)), f.x), f.y); }
  float fbm(vec2 p){ float v=0., a=.5; for(int i=0;i<4;i++){ v+=a*noise(p); p*=2.03; a*=.5; } return v; }
`;

const PHOTO_VERT = /* glsl */`
  varying vec2 vUv; varying vec3 vWorld;
  void main(){ vUv = uv; vec4 w = modelMatrix * vec4(position,1.); vWorld = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }
`;

const PHOTO_FRAG = /* glsl */`
  uniform sampler2D map; uniform float loaded, reveal, exitT, modeIn, modeOut, time, aspect, reflectAmount, hover, hazeDensity;
  uniform vec3 hazeColor;
  varying vec2 vUv; varying vec3 vWorld;
  ${NOISE_GLSL}
  const vec3 GOLD = vec3(2.6, 1.7, .7);
  void main(){
    vec2 uv = vUv;
    if (reflectAmount > 0.) uv.y = (1. - vUv.y) * .85;
    float alpha = 1.; vec3 edge = vec3(0.);
    vec2 p = vec2((uv.x - .5) * aspect, uv.y - .5);

    // Arrival. Skipped entirely once settled, so a resting photo costs one texture read.
    if (reveal < .999) {
    if (modeIn < .5) {                     // ink bleeding into paper
      float n = fbm(uv * vec2(aspect, 1.) * 4.2);
      float th = reveal * 1.34 - .17;
      alpha *= smoothstep(n - .05, n + .05, th);
      edge += GOLD * smoothstep(.11, 0., abs(n - th)) * step(.001, reveal) * step(reveal, .995);
    } else if (modeIn < 1.5) {             // shoji sliding apart from centre
      float d = abs(uv.x - .5) * 2.;
      float cols = floor(uv.x * 8.);
      float th = reveal * 1.25 - hash(vec2(cols, 3.)) * .25 * (1. - reveal);
      alpha *= smoothstep(th, th - .02, d);
      edge += GOLD * smoothstep(.05, 0., abs(d - th)) * step(reveal, .995);
    } else if (modeIn < 2.5) {             // lightning wipe on a jagged diagonal
      float jag = (noise(vec2(uv.y * 26., 7.)) - .5) * .09;
      float d = (uv.x + uv.y * .55) / 1.55 + jag;
      float th = reveal * 1.2 - .1;
      alpha *= smoothstep(th + .012, th - .012, d);
      edge += vec3(5., 4.2, 2.2) * smoothstep(.022, 0., abs(d - th)) * step(reveal, .995);
    } else {                               // iris opening from the centre
      float d = length(p) / (.5 * length(vec2(aspect, 1.)));
      d += (fbm(uv * 7.) - .5) * .16;
      float th = reveal * 1.24;
      alpha *= smoothstep(th, th - .03, d);
      edge += GOLD * smoothstep(.06, 0., abs(d - th)) * step(reveal, .995);
    }

    }

    // Departure
    if (exitT > 0.) {
      if (modeOut < .5) {                  // cut in two along a diagonal
        vec2 n = normalize(vec2(.55, 1.));
        float side = dot(p, n) + (noise(vec2(dot(p, vec2(n.y, -n.x)) * 22., 2.)) - .5) * .012;
        float open = smoothstep(.12, 1., exitT);
        vec2 shift = n * sign(side) * open * .62 + vec2(n.y, -n.x) * sign(side) * open * .16;
        uv -= vec2(shift.x / aspect, shift.y);
        alpha *= step(0., uv.x) * step(uv.x, 1.) * step(0., uv.y) * step(uv.y, 1.);
        // Pixels in the widening gap would otherwise sample across the cut.
        vec2 moved = vec2((uv.x - .5) * aspect, uv.y - .5);
        alpha *= step(0., dot(moved, n) * sign(side));
        alpha *= 1. - smoothstep(.6, 1., exitT);
        edge += vec3(7., 6., 3.) * smoothstep(.016, 0., abs(side)) * (1. - smoothstep(.03, .3, exitT)) * smoothstep(0., .03, exitT);
      } else if (modeOut < 1.5) {          // burning away from the edges
        float n = fbm(uv * vec2(aspect, 1.) * 5.) + (length(p) * .62);
        float th = 1.28 - exitT * 1.3;
        alpha *= smoothstep(th + .02, th - .02, n);
        float band = smoothstep(.1, 0., abs(n - th));
        edge += vec3(5.5, 2.1, .4) * band;
      } else if (modeOut < 2.5) {          // lifts away behind a light sweep
        alpha *= 1. - smoothstep(.55, 1., exitT);
      } else {                             // slats sliding opposite ways
        float slat = floor(uv.y * 14.);
        float dir = mod(slat, 2.) * 2. - 1.;
        float delay = hash(vec2(slat, 9.)) * .3;
        uv.x += dir * smoothstep(delay, delay + .7, exitT) * 1.1;
        alpha *= step(0., uv.x) * step(uv.x, 1.);
        edge += GOLD * .35 * smoothstep(.0, .3, exitT) * (1. - smoothstep(.5, .95, exitT)) * smoothstep(.46, .5, abs(fract(uv.y * 14.) - .5));
      }
    }

    vec3 c = texture2D(map, uv).rgb;
    if (loaded < .5) c = vec3(.09, .05, .03);
    float sweep = smoothstep(.09, 0., abs((vUv.x + vUv.y * .5) * .66 - (reveal * 1.5 - .25))) * step(reveal, .995);
    c += vec3(1., .75, .42) * sweep * .6;
    vec2 q = vUv - .5;
    c *= 1. - dot(q, q) * .36;
    c += vec3(.05, .036, .02) * hover;
    c += edge * step(.001, reveal);

    if (reflectAmount > 0.) {
      alpha *= reflectAmount * pow(vUv.y, 2.2);
      gl_FragColor = vec4(c, alpha);
    } else {
      if (alpha < .004) discard;
      float f = 1. - exp(-pow(hazeDensity * length(vWorld - cameraPosition), 2.));
      gl_FragColor = vec4(mix(c, hazeColor, f), alpha);
    }
  }
`;

const SKY_FRAG = /* glsl */`
  varying vec3 vDir; uniform float time, flash;
  ${NOISE_GLSL}
  void main(){
    vec3 d = normalize(vDir);
    #ifdef LITE
    float haze = .55;
    #else
    float haze = fbm(vec2(atan(d.z, d.x) * 2.2, d.y * 3.2) + time * .012);
    #endif
    vec3 deep = vec3(.012, .009, .022), warm = vec3(.2, .068, .024), rust = vec3(.36, .13, .04);
    float band = pow(1. - abs(d.y), 3.);
    vec3 c = mix(deep, warm, band * (.42 + haze * .85));
    c += rust * pow(band, 3.) * haze * .55;
    c += vec3(.8, .75, .55) * flash * .5;
    gl_FragColor = vec4(c, 1.);
  }
`;

const BLOOM_PICK_FRAG = /* glsl */`
  uniform sampler2D tex; varying vec2 vUv;
  void main(){ vec3 c = texture2D(tex, vUv).rgb; float b = max(c.r, max(c.g, c.b));
    gl_FragColor = vec4(c * smoothstep(.95, 1.8, b), 1.); }
`;
const BLUR_FRAG = /* glsl */`
  uniform sampler2D tex; uniform vec2 dir; varying vec2 vUv;
  void main(){ vec3 c = texture2D(tex, vUv).rgb * .227;
    c += (texture2D(tex, vUv + dir * 1.385).rgb + texture2D(tex, vUv - dir * 1.385).rgb) * .316;
    c += (texture2D(tex, vUv + dir * 3.231).rgb + texture2D(tex, vUv - dir * 3.231).rgb) * .07;
    gl_FragColor = vec4(c, 1.); }
`;
const COMPOSITE_FRAG = /* glsl */`
  uniform sampler2D scene, bloomA, bloomB; uniform float time, flash, speed, bloomGain, fade;
  uniform vec2 centre; varying vec2 vUv;
  ${NOISE_GLSL}
  vec3 sampleScene(vec2 uv){
    if (speed < .004) return texture2D(scene, uv).rgb;
    vec2 d = (uv - centre) * speed * .07;
    vec3 c = vec3(0.);
    for (int i = 0; i < 9; i++) c += texture2D(scene, uv - d * float(i) / 8.).rgb;
    return c / 9.;
  }
  vec3 shoulder(vec3 c){ const float k = .78; return mix(c, k + (1. - k) * (1. - exp(-(c - k) / (1. - k))), step(k, c)); }
  void main(){
    #ifdef LITE
    vec3 c = texture2D(scene, vUv).rgb + texture2D(bloomA, vUv).rgb * bloomGain * 1.5;
    #else
    float ab = .0009 + speed * .007;
    vec2 off = (vUv - centre) * ab;
    vec3 c = vec3(sampleScene(vUv + off).r, sampleScene(vUv).g, sampleScene(vUv - off).b);
    c += (texture2D(bloomA, vUv).rgb * .75 + texture2D(bloomB, vUv).rgb) * bloomGain;
    #endif
    vec2 q = vUv - .5;
    c *= 1. - smoothstep(.2, .95, length(q) * 1.25) * .55;
    c += vec3(1., .94, .78) * flash;
    c = shoulder(c) * fade;
    c = mix(12.92 * c, 1.055 * pow(max(c, vec3(.0001)), vec3(1. / 2.4)) - .055, step(.0031308, c));
    c += (hash(vUv * 917. + fract(time) * 31.) - .5) * .022;
    gl_FragColor = vec4(c, 1.);
  }
`;
const FULLSCREEN_VERT = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0., 1.); }`;

/* ---------- sound ---------- */

class Sound {
  constructor(muted) {
    this.muted = muted;
    this.accents = 0;
    this.lastAccent = -Infinity;
    const Context = window.AudioContext || window.webkitAudioContext;
    if (!Context) return;
    this.ctx = new Context();
    this.master = this.ctx.createGain();
    this.master.gain.value = muted ? 0 : 1;
    this.master.connect(this.ctx.destination);
    const length = this.ctx.sampleRate * 2;
    this.noise = this.ctx.createBuffer(1, length, this.ctx.sampleRate);
    const data = this.noise.getChannelData(0);
    for (let i = 0; i < length; i++) data[i] = Math.random() * 2 - 1;
    const wind = this.ctx.createBufferSource();
    wind.buffer = this.noise; wind.loop = true;
    this.windFilter = this.ctx.createBiquadFilter();
    this.windFilter.type = 'bandpass'; this.windFilter.frequency.value = 500; this.windFilter.Q.value = .7;
    this.windGain = this.ctx.createGain(); this.windGain.gain.value = 0;
    wind.connect(this.windFilter).connect(this.windGain).connect(this.master);
    wind.start();
    fetch(BIWA).then(r => r.arrayBuffer()).then(b => this.ctx.decodeAudioData(b)).then(buffer => { this.biwa = buffer; }).catch(() => {});
    this.ctx.resume?.();
  }
  setMuted(muted) {
    this.muted = muted;
    if (this.master) this.master.gain.setTargetAtTime(muted ? 0 : 1, this.ctx.currentTime, .05);
  }
  strum(rate = 1, gain = .5) {
    if (!this.biwa) return;
    const source = this.ctx.createBufferSource();
    source.buffer = this.biwa; source.playbackRate.value = rate;
    const g = this.ctx.createGain(); g.gain.value = gain;
    source.connect(g).connect(this.master);
    source.start();
  }
  // The string is a treat, not a click sound: a few per visit, spaced well apart.
  accent(rate, gain) {
    const now = performance.now();
    if (this.accents >= MAX_ACCENTS || now - this.lastAccent < ACCENT_GAP_MS) return;
    this.accents++;
    this.lastAccent = now;
    this.strum(rate, gain);
  }
  crack(gain = .5) {
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    const source = this.ctx.createBufferSource();
    source.buffer = this.noise;
    const filter = this.ctx.createBiquadFilter();
    filter.type = 'highpass';
    filter.frequency.setValueAtTime(3200, now);
    filter.frequency.exponentialRampToValueAtTime(240, now + .32);
    const g = this.ctx.createGain();
    g.gain.setValueAtTime(gain, now);
    g.gain.exponentialRampToValueAtTime(.001, now + .55);
    source.connect(filter).connect(g).connect(this.master);
    source.start(now, Math.random());
    source.stop(now + .6);
  }
  wind(speed) {
    if (!this.windGain) return;
    const now = this.ctx.currentTime;
    this.windGain.gain.setTargetAtTime(clamp(speed) * .16, now, .1);
    this.windFilter.frequency.setTargetAtTime(380 + clamp(speed) * 1500, now, .12);
  }
  dispose() { this.ctx?.close?.(); }
}

/* ---------- instanced kit: collects boxes, then builds one draw call per material ---------- */

class Kit {
  constructor() { this.lists = { wood: [], lacquer: [], shoji: [], tatami: [], plank: [], lantern: [] }; this.halos = []; }
  add(kind, parent, x, y, z, sx, sy, sz, shade = 1, rotation = null) {
    const m = new THREE.Matrix4().compose(v3(x, y, z), rotation || new THREE.Quaternion(), v3(sx, sy, sz));
    this.lists[kind].push({ matrix: new THREE.Matrix4().multiplyMatrices(parent, m), shade });
  }
  build(geometry, material, kind) {
    const list = this.lists[kind];
    const mesh = new THREE.InstancedMesh(geometry, material, list.length);
    const color = new THREE.Color();
    list.forEach((item, i) => {
      mesh.setMatrixAt(i, item.matrix);
      if (Array.isArray(item.shade)) color.setRGB(...item.shade);
      else color.setRGB(item.shade, item.shade, item.shade);
      mesh.setColorAt(i, color);
    });
    mesh.frustumCulled = false;
    return mesh;
  }
}

const scratchQuat = new THREE.Quaternion();
const AXIS_X = v3(1, 0, 0), AXIS_Y = v3(0, 1, 0), AXIS_Z = v3(0, 0, 1);

function addLantern(kit, parent, x, y, z, rope) {
  kit.add('wood', parent, x, y + rope / 2 + .4, z, .035, rope, .035, .6);
  kit.add('lantern', parent, x, y, z, .42, .52, .42, 1);
  kit.add('wood', parent, x, y + .55, z, .36, .08, .36, .5);
  kit.add('wood', parent, x, y - .55, z, .3, .06, .3, .5);
  const p = v3(x, y, z).applyMatrix4(parent);
  kit.halos.push(p.x, p.y, p.z);
}

// One hall: floor, walls of lit paper, coffered ceiling, tiered roof seen from the void.
function buildHall(kit, parent, station, rand) {
  const { w, d, h } = HALL;
  const rail = h * .74;
  const shade = () => rand(.72, 1.12);

  // Floor. A hall that drops the visitor gets animated leaves over its front part.
  const fixedDepth = station.outKind === 'fall' ? 4 : d;
  kit.add('plank', parent, 0, -.22, fixedDepth / 2, w + 1.2, .44, fixedDepth, 1);
  const mats = station.outKind === 'fall' ? 2 : 4;
  const matW = 2.5, matD = fixedDepth / mats;
  for (let row = 0; row < mats; row++) {
    for (let col = -2; col <= 2; col++) {
      kit.add('tatami', parent, col * (matW + .03), .012, (row + .5) * matD, matW, .02, matD - .03, rand(.84, 1.06));
    }
  }
  // Underside beams and edge timbers
  for (const x of [-w / 2 - .4, w / 2 + .4]) kit.add('wood', parent, x, -.52, d / 2, .7, .9, d + 1.4, .8);
  for (let i = 0; i < 5; i++) kit.add('wood', parent, 0, -.74, i * d / 4, w + 1, .5, .5, .7);

  // Posts along back and sides
  for (const x of [-w / 2, -w / 6, w / 6, w / 2]) kit.add('wood', parent, x, h / 2, 0, .44, h, .44, shade());
  for (const side of [-1, 1]) {
    for (const z of [d / 3, 2 * d / 3, d]) kit.add('wood', parent, side * w / 2, h / 2, z, .4, h, .4, shade());
    kit.add('lacquer', parent, side * w / 2, rail, d / 2, .34, .42, d + .4, 1);
    kit.add('wood', parent, side * w / 2, h - .3, d / 2, .5, .6, d + .5, .9);
    kit.add('wood', parent, side * w / 2, .18, d * .34, .4, .36, d * .68, .85);
  }
  kit.add('lacquer', parent, 0, rail, 0, w + .5, .46, .4, 1);
  kit.add('wood', parent, 0, h - .3, 0, w + .6, .6, .6, .9);
  kit.add('wood', parent, 0, h - .3, d, w + .6, .6, .5, .9);

  // Lit walls. Left/right back bays are paper; the central bay holds the sliding doors.
  const bayW = w / 3;
  for (const side of [-1, 1]) {
    kit.add('shoji', parent, side * bayW, rail / 2, -.04, bayW - .44, rail - .1, .06, rand(1.2, 1.9));
    kit.add('shoji', parent, side * w / 2, rail / 2, d / 6, .06, rail - .1, d / 3 - .4, rand(1.1, 1.8));
    // Middle side bay half open onto the void.
    kit.add('shoji', parent, side * w / 2, rail / 2, d / 2 - d / 12, .06, rail - .1, d / 6 - .2, rand(1, 1.6));
  }
  // Transom lattice above the rail
  for (let x = -7; x <= 7; x++) kit.add('shoji', parent, x * w / 15, (rail + h - .6) / 2 + .1, -.06, w / 15 - .12, h - rail - .95, .05, .55 + (x % 2 ? .18 : 0));
  for (const side of [-1, 1]) for (let z = 0; z < 6; z++) kit.add('shoji', parent, side * w / 2, (rail + h - .6) / 2 + .1, z * d / 6 + d / 12, .05, h - rail - .95, d / 6 - .12, .55);

  // Coffered ceiling
  kit.add('wood', parent, 0, h + .06, d / 2, w + .4, .12, d + .4, .34);
  for (let i = 0; i <= 8; i++) kit.add('wood', parent, -w / 2 + i * w / 8, h - .1, d / 2, .15, .2, d, .72);
  for (let i = 0; i <= 6; i++) kit.add('wood', parent, 0, h - .1, i * d / 6, w, .2, .15, .72);

  // Tiered roof, only readable from outside
  for (let tier = 0; tier < 3; tier++) {
    const y = h + .55 + tier * 1.25, scale = 1 - tier * .24;
    kit.add('wood', parent, 0, y, d / 2, (w + 4) * scale, .3, (d + 4) * scale, .5);
    kit.add('lacquer', parent, 0, y + .36, d / 2, (w + 1.6) * scale, .42, (d + 1.6) * scale, .75);
  }

  // Lanterns, kept near the side walls so they never cross the photo
  for (const z of [d * .32, d * .8]) for (const side of [-1, 1]) addLantern(kit, parent, side * (w / 2 - 1.7), h - 2.5 - rand(0, 1), z, 2 + rand(0, 1));
}

// Distant fragments of the castle hanging at impossible angles.
function buildFragment(kit, parent, rand) {
  const w = rand(8, 20), d = rand(6, 15), h = rand(4, 9);
  kit.add('wood', parent, 0, -.2, 0, w, .4, d, rand(.5, .85));
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) kit.add('wood', parent, sx * w / 2, h / 2, sz * d / 2, .4, h, .4, .7);
  kit.add('wood', parent, 0, h, 0, w + 1.5, .34, d + 1.5, .55);
  kit.add('lacquer', parent, 0, h + .4, 0, w + .4, .3, d + .4, .55);
  const panels = Math.max(2, Math.round(w / 2.6));
  for (let i = 0; i < panels; i++) {
    const glow = rand() > .28 ? rand(1, 2.3) : .22;
    kit.add('shoji', parent, -w / 2 + (i + .5) * w / panels, h / 2, -d / 2, w / panels - .08, h - .25, .06, glow);
    if (rand() > .45) kit.add('shoji', parent, -w / 2 + (i + .5) * w / panels, h / 2, d / 2, w / panels - .08, h - .25, .06, rand(.8, 1.9));
  }
  if (rand() > .4) {
    const steps = Math.round(rand(9, 24));
    const dir = rand() > .5 ? 1 : -1;
    for (let i = 0; i < steps; i++) kit.add('wood', parent, dir * (w / 2 + 1.4 + i * .62), -.3 - i * .42, 0, .68, .2, 3, rand(.6, .95));
  }
  if (rand() > .55) addLantern(kit, parent, 0, h - 1.3, 0, .9);
}

function quatFromEuler(x, y, z) {
  return new THREE.Quaternion().setFromEuler(new THREE.Euler(x, y, z));
}

/* ---------- the experience ---------- */

export async function openCastle({ photos, trigger }) {
  ensureStylesheet();
  if (photos.length <= PHOTOS_PER_ROOM || matchMedia('(prefers-reduced-motion: reduce)').matches || !webglAvailable()) {
    return openPlainGallery(photos, trigger);
  }
  const lite = detectLite();
  let spriteSet;
  try {
    spriteSet = await loadSprites(lite);
  } catch {
    return openPlainGallery(photos, trigger);
  }
  return startExperience(photos, trigger, spriteSet, lite);
}

function ensureStylesheet() {
  if (document.querySelector('link[data-castle]')) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = STYLESHEET;
  link.dataset.castle = '';
  document.head.append(link);
}

function webglAvailable() {
  try {
    return !!document.createElement('canvas').getContext('webgl2');
  } catch { return false; }
}

function loadSprites(lite) {
  const loader = new THREE.TextureLoader();
  return Promise.all(Object.entries(SPRITES).map(([name, sprite]) => new Promise((resolve, reject) => {
    loader.load(lite ? sprite.lite : sprite.src, texture => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = lite ? 1 : 4;
      texture.repeat.set(1 / sprite.cols, 1 / sprite.rows);
      resolve([name, texture]);
    }, undefined, reject);
  }))).then(Object.fromEntries);
}

function lockPage() {
  const root = document.documentElement;
  const previous = { overflow: root.style.overflow, bodyOverflow: document.body.style.overflow };
  root.style.overflow = 'hidden';
  document.body.style.overflow = 'hidden';
  root.classList.add('in-castle');
  window.dispatchEvent(new Event('castle:enter'));
  return () => {
    root.style.overflow = previous.overflow;
    document.body.style.overflow = previous.bodyOverflow;
    root.classList.remove('in-castle');
    window.dispatchEvent(new Event('castle:leave'));
  };
}

function trapFocus(root, event) {
  if (event.key !== 'Tab') return;
  const items = [...root.querySelectorAll('button:not([hidden]),a[href]')].filter(el => el.offsetParent !== null);
  if (!items.length) return;
  const first = items[0], last = items[items.length - 1];
  if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
  else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
}

// Reduced motion, or no WebGL: same photographs, nothing moving.
function openPlainGallery(photos, trigger) {
  const unlock = lockPage();
  const root = document.createElement('div');
  root.className = 'castle castle-plain';
  root.setAttribute('role', 'dialog');
  root.setAttribute('aria-modal', 'true');
  root.setAttribute('aria-label', 'Photo gallery');
  const close = document.createElement('button');
  close.type = 'button';
  close.className = 'castle-button castle-close';
  close.textContent = 'Close';
  const grid = document.createElement('div');
  grid.className = 'castle-grid';
  for (const photo of photos) {
    const figure = document.createElement('figure');
    const image = document.createElement('img');
    image.src = photo.src; image.alt = photo.alt; image.loading = 'lazy';
    image.width = photo.fullWidth; image.height = photo.fullHeight;
    const caption = document.createElement('figcaption');
    caption.textContent = photo.alt;
    figure.append(image, caption);
    grid.append(figure);
  }
  root.append(close, grid);
  document.body.append(root);
  close.focus({ preventScroll: true });
  const done = () => {
    document.removeEventListener('keydown', onKey);
    root.remove();
    unlock();
    trigger?.focus({ preventScroll: true });
  };
  function onKey(event) {
    if (event.key === 'Escape') done();
    else trapFocus(root, event);
  }
  close.addEventListener('click', done);
  document.addEventListener('keydown', onKey);
}

function startExperience(photos, trigger, spriteSet, lite) {
  textureAnisotropy = lite ? 2 : 8;
  const photoCount = photos.length;
  const stops = [];
  photos.forEach((photo, photoIndex) => {
    const stop = Math.floor(photoIndex / PHOTOS_PER_ROOM);
    (stops[stop] = stops[stop] || []).push({ ...photo, photoIndex });
  });
  // N counts the stops on the route; each one hangs up to three photographs.
  const N = stops.length;
  const rooms = N;
  const unlock = lockPage();
  const abort = new AbortController();
  const listen = { signal: abort.signal };
  let muted = false;
  try { muted = localStorage.getItem('castle-muted') === '1'; } catch {}
  const sound = new Sound(muted);

  /* ----- DOM shell ----- */

  const root = document.createElement('div');
  root.className = 'castle';
  root.setAttribute('role', 'dialog');
  root.setAttribute('aria-modal', 'true');
  root.setAttribute('aria-label', `Photo gallery, ${photoCount} photographs in ${N} rooms. Scroll or use the up and down arrow keys to change room, left and right arrow keys to change photograph.`);
  root.innerHTML = `
    <div class="castle-world"><canvas class="castle-canvas" aria-hidden="true"></canvas></div>
    <div class="castle-scroll" tabindex="-1"><div class="castle-spacer"></div></div>
    <div class="castle-ui" hidden>
      <div class="castle-roomcard" aria-hidden="true"><span class="castle-roomcard-numeral"></span><span class="castle-roomcard-label"></span></div>
      <div class="castle-title" aria-hidden="true"><span class="castle-title-line"></span><span class="castle-title-sub">${photoCount} photographs</span></div>
      <div class="castle-topbar">
        <p class="castle-room" aria-hidden="true"><span class="castle-room-numeral"></span><span class="castle-room-text"></span></p>
        <div class="castle-actions">
          <button type="button" class="castle-button castle-sound"></button>
          <button type="button" class="castle-button castle-close">Close</button>
        </div>
      </div>
      <div class="castle-caption" aria-live="polite">
        <p class="castle-count"><span class="castle-count-now"></span><span class="castle-count-all">/ ${String(photoCount).padStart(2, '0')}</span></p>
        <p class="castle-alt"></p>
      </div>
      <nav class="castle-rail" aria-label="Choose a room"></nav>
      <div class="castle-picks" role="group" aria-label="Photographs in this room"></div>
      <p class="castle-tip" aria-hidden="true"></p>
      <div class="castle-nav">
        <button type="button" class="castle-button castle-enlarge">Enlarge</button>
        <button type="button" class="castle-button castle-prev" aria-label="Previous room">↑</button>
        <button type="button" class="castle-button castle-next" aria-label="Next room">↓</button>
      </div>
      <p class="castle-hint" aria-hidden="true"><span>Scroll</span><i></i></p>
      <div class="castle-end" hidden>
        <p>That's the whole castle.</p>
        <button type="button" class="castle-button castle-exit">Back to the story</button>
      </div>
      <button type="button" class="castle-button castle-skip">Skip intro</button>
    </div>
    <svg class="castle-cut" aria-hidden="true"><polyline class="castle-cut-glow"/><polyline class="castle-cut-core"/><line class="castle-cut-a"/><line class="castle-cut-b"/></svg>
    <div class="castle-flash" aria-hidden="true"></div>
    <div class="castle-pagehero" aria-hidden="true"></div>`;
  document.body.append(root);

  const q = selector => root.querySelector(selector);
  q('.castle-world').style.clipPath = 'polygon(0 0,0 0,0 0)';
  const world = q('.castle-world'), canvas = q('.castle-canvas'), scroller = q('.castle-scroll'), spacer = q('.castle-spacer');
  const ui = q('.castle-ui'), cutSvg = q('.castle-cut'), flashEl = q('.castle-flash'), pageHero = q('.castle-pagehero');
  const caption = q('.castle-caption'), altEl = q('.castle-alt'), countEl = q('.castle-count-now');
  const roomEl = q('.castle-room'), roomNumeral = q('.castle-room-numeral'), roomText = q('.castle-room-text');
  const roomCard = q('.castle-roomcard'), hint = q('.castle-hint'), endCard = q('.castle-end');
  const title = q('.castle-title'), titleLine = q('.castle-title-line'), skipButton = q('.castle-skip');
  const closeButton = q('.castle-close'), soundButton = q('.castle-sound'), enlargeButton = q('.castle-enlarge');
  const rail = q('.castle-rail');
  [...'Gallery'].forEach((letter, i) => {
    const span = document.createElement('span');
    span.textContent = letter;
    span.style.setProperty('--i', i);
    titleLine.append(span);
  });
  const updateSoundLabel = () => {
    soundButton.textContent = sound.muted ? 'Sound off' : 'Sound on';
    soundButton.setAttribute('aria-pressed', String(!sound.muted));
  };
  updateSoundLabel();

  const picks = q('.castle-picks'), tip = q('.castle-tip');
  tip.textContent = matchMedia('(pointer: coarse)').matches ? 'Tap a photo · swipe to switch · scroll for next room' : 'Click a photo to bring it forward';
  const ticks = stops.map((stop, i) => {
    const tick = document.createElement('button');
    tick.type = 'button';
    tick.className = 'castle-tick';
    tick.dataset.room = '';
    tick.setAttribute('aria-label', `Room ${i + 1} of ${N}`);
    tick.addEventListener('click', () => goTo(i), listen);
    rail.append(tick);
    return tick;
  });

  /* ----- renderer and post ----- */

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: lite ? 'default' : 'high-performance', stencil: false });
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.autoClear = true;
  let pixelRatio = Math.min(window.devicePixelRatio || 1, lite ? 1.25 : 1.75);

  const scene = new THREE.Scene();
  const hazeColor = new THREE.Color(.05, .022, .014);
  scene.fog = new THREE.FogExp2(hazeColor, .0046);
  const camera = new THREE.PerspectiveCamera(38, 1, .2, 900);

  const renderTarget = new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, samples: lite ? 0 : 4 });
  const bloomTargets = [0, 1, 2, 3].map(() => new THREE.WebGLRenderTarget(4, 4, { type: THREE.HalfFloatType, depthBuffer: false }));
  const quadScene = new THREE.Scene();
  const quadCamera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2));
  quad.frustumCulled = false;
  quadScene.add(quad);
  const liteDefines = lite ? { LITE: 1 } : {};
  const quadMaterial = (fragmentShader, uniforms) => new THREE.ShaderMaterial({ vertexShader: FULLSCREEN_VERT, fragmentShader, uniforms, depthTest: false, depthWrite: false, defines: liteDefines });
  const pickMaterial = quadMaterial(BLOOM_PICK_FRAG, { tex: { value: null } });
  const blurMaterial = quadMaterial(BLUR_FRAG, { tex: { value: null }, dir: { value: new THREE.Vector2() } });
  const compositeMaterial = quadMaterial(COMPOSITE_FRAG, {
    scene: { value: renderTarget.texture }, bloomA: { value: bloomTargets[1].texture }, bloomB: { value: bloomTargets[3].texture },
    time: { value: 0 }, flash: { value: 0 }, speed: { value: 0 }, bloomGain: { value: .8 }, fade: { value: 1 }, centre: { value: new THREE.Vector2(.5, .5) },
  });
  const drawQuad = (material, target) => {
    quad.material = material;
    renderer.setRenderTarget(target);
    renderer.render(quadScene, quadCamera);
  };

  /* ----- shared materials ----- */

  const texScale = lite ? .5 : 1;
  const woodMap = canvasTexture(1024 * texScale, 512 * texScale, paintWood, { repeat: true });
  const lacquerMap = canvasTexture(512 * texScale, 256 * texScale, (c, w, h) => paintWood(c, w, h, [92, 26, 13]), { repeat: true });
  const plankMap = canvasTexture(1024 * texScale, 1024 * texScale, (c, w, h) => {
    paintWood(c, w, h, [66, 36, 20]);
    c.fillStyle = 'rgba(10,4,2,.85)';
    for (let i = 0; i < 12; i++) c.fillRect(0, i * h / 12, w, 3);
  }, { repeat: true });
  plankMap.repeat.set(3, 3);
  const shojiMap = canvasTexture(lite ? 384 : 512, lite ? 768 : 1024, paintShoji);
  const tatamiMap = canvasTexture(512 * texScale, 512 * texScale, paintTatami);
  const glowMap = canvasTexture(128, 128, paintGlow);

  const surface = params => {
    if (!lite) return new THREE.MeshStandardMaterial(params);
    const { roughness, metalness, ...basic } = params;
    return new THREE.MeshLambertMaterial(basic);
  };
  const woodMaterial = surface({ map: woodMap, roughness: .62, metalness: .04 });
  const lacquerMaterial = surface({ map: lacquerMap, roughness: .32, metalness: .12, color: 0xffffff });
  const plankMaterial = surface({ map: plankMap, roughness: .3, metalness: .05 });
  const tatamiMaterial = surface({ map: tatamiMap, roughness: .9 });
  const shojiColor = new THREE.Color(.8, .66, .54);
  const shojiMaterial = new THREE.MeshBasicMaterial({ map: shojiMap, color: shojiColor, toneMapped: false });
  const lanternMaterial = new THREE.MeshBasicMaterial({ color: new THREE.Color(5.2, 2.9, 1.25), toneMapped: false });
  const goldMaterial = surface({ color: lite ? 0xe8b45c : 0xd9a24d, roughness: .3, metalness: .95, emissive: 0x5c3510, emissiveIntensity: lite ? 1 : .55 });
  const frameMaterial = surface({ map: lacquerMap, color: 0x4a3028, roughness: .3, metalness: .1 });
  const matMaterial = surface({ color: 0x1a0d09, roughness: .85 });

  scene.add(new THREE.HemisphereLight(0xffb27a, 0x2a1016, .92));
  const roomLight = new THREE.PointLight(0xffb066, 95, 42, 1.7);
  const frameLight = new THREE.PointLight(0xffd8a0, 42, 15, 1.8);
  scene.add(roomLight);
  if (!lite) scene.add(frameLight);

  const skyUniforms = { time: { value: 0 }, flash: { value: 0 } };
  const sky = new THREE.Mesh(new THREE.SphereGeometry(760, lite ? 16 : 32, lite ? 10 : 20), new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, uniforms: skyUniforms, fragmentShader: SKY_FRAG, defines: liteDefines,
    vertexShader: 'varying vec3 vDir; void main(){ vDir = position; gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(position,1.); }',
  }));
  sky.frustumCulled = false;
  scene.add(sky);

  /* ----- lay out the route ----- */

  const box = new THREE.BoxGeometry(1, 1, 1);
  const kit = new Kit();
  const rand = makeRandom(4242);
  const stations = [];
  let position = v3();
  let orientation = new THREE.Quaternion();
  // Each stop leaves differently: burn, cut, slats, cut, lift, then repeats.
  const EXITS = [1, 0, 3, 0, 2];
  const KINDS = ['through', 'fall', 'turn', 'barrel', 'fall'];
  for (let i = 0; i < N; i++) {
    const outKind = KINDS[i % KINDS.length];
    const side = i % 4 < 2 ? 1 : -1;
    stations.push({
      index: i, photos: stops[i], room: i, outKind, side,
      pos: position.clone(), quat: orientation.clone(),
      modeOut: EXITS[i % EXITS.length],
    });
    let localOffset, turn;
    if (outKind === 'through') { localOffset = v3(side * 7, -3.5, -52); turn = new THREE.Quaternion(); }
    else if (outKind === 'turn') { localOffset = v3(side * 52, -5, 14); turn = quatFromEuler(0, -side * Math.PI / 2, 0); }
    else if (outKind === 'fall') { localOffset = v3(side * 5, -58, -20); turn = quatFromEuler(0, side * .35, 0); }
    else { localOffset = v3(side * 13, -6, -54); turn = quatFromEuler(0, 0, side * Math.PI / 2); }
    position = position.clone().add(localOffset.applyQuaternion(orientation));
    orientation = orientation.clone().multiply(turn).normalize();
  }

  const stationMatrix = station => new THREE.Matrix4().compose(station.pos, station.quat, v3(1, 1, 1));
  stations.forEach(station => buildHall(kit, stationMatrix(station), station, rand));

  // Fragments fill the void; keep them clear of the route so nothing blocks the view.
  const routeBox = new THREE.Box3();
  stations.forEach(station => routeBox.expandByPoint(station.pos));
  routeBox.expandByScalar(170);
  const axisTurns = [
    [0, 0, 0], [Math.PI, 0, 0], [Math.PI / 2, 0, 0], [-Math.PI / 2, 0, 0], [0, 0, Math.PI / 2], [0, 0, -Math.PI / 2],
    [Math.PI / 2, 0, Math.PI / 2], [0, Math.PI / 2, Math.PI / 2],
  ];
  const fragmentCount = lite ? 70 : 240;
  let placed = 0, tries = 0;
  while (placed < fragmentCount && tries++ < fragmentCount * 12) {
    const p = v3(rand(routeBox.min.x, routeBox.max.x), rand(routeBox.min.y, routeBox.max.y), rand(routeBox.min.z, routeBox.max.z));
    if (stations.some(station => station.pos.distanceTo(p) < 46)) continue;
    const turnEuler = axisTurns[Math.floor(rand(0, axisTurns.length))];
    const matrix = new THREE.Matrix4().compose(p, quatFromEuler(turnEuler[0], turnEuler[1] + Math.round(rand(0, 3)) * Math.PI / 2, turnEuler[2]), v3(1, 1, 1));
    buildFragment(kit, matrix, rand);
    placed++;
  }

  // Three great gates the opening falls through.
  const gates = [185, 128, 72].map(height => {
    const group = new THREE.Group();
    const leaves = [-1, 1].map(side => {
      const leaf = new THREE.Mesh(box, shojiMaterial);
      leaf.scale.set(15, .2, 30);
      leaf.position.x = side * 7.5;
      group.add(leaf);
      return { mesh: leaf, side };
    });
    const bar = (x, z, sx, sz) => {
      const beam = new THREE.Mesh(box, woodMaterial);
      beam.position.set(x, 0, z); beam.scale.set(sx, 1.2, sz);
      group.add(beam);
    };
    bar(0, -15.6, 33, 1.6); bar(0, 15.6, 33, 1.6); bar(-15.6, 0, 1.6, 33); bar(15.6, 0, 1.6, 33);
    scene.add(group);
    return { group, leaves, height, opened: false };
  });

  const boxInstanced = kind => kit.build(box, { wood: woodMaterial, lacquer: lacquerMaterial, shoji: shojiMaterial, tatami: tatamiMaterial, plank: plankMaterial, lantern: lanternMaterial }[kind], kind);
  ['wood', 'lacquer', 'shoji', 'tatami', 'plank', 'lantern'].forEach(kind => { if (kit.lists[kind].length) scene.add(boxInstanced(kind)); });
  const halos = new THREE.Points(
    new THREE.BufferGeometry().setAttribute('position', new THREE.Float32BufferAttribute(kit.halos, 3)),
    new THREE.PointsMaterial({ map: glowMap, color: new THREE.Color(1.6, .85, .36), size: 7, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true, toneMapped: false, fog: false }),
  );
  halos.frustumCulled = false;
  scene.add(halos);

  /* ----- per-station moving parts: doors, floor leaves, framed photograph ----- */

  const textureLoader = new THREE.TextureLoader();
  const placeholder = new THREE.DataTexture(new Uint8Array([24, 13, 8, 255]), 1, 1);
  placeholder.needsUpdate = true;

  function photoSize(aspect) {
    const maxW = 6.6, maxH = 5.4;
    return aspect >= maxW / maxH ? { pw: maxW, ph: maxW / aspect } : { pw: maxH * aspect, ph: maxH };
  }

  function buildFramedPhoto(station, photo, slot) {
    const aspect = photo.fullWidth / photo.fullHeight;
    const { pw, ph } = photoSize(aspect);
    const fw = pw + .84, fh = ph + .84;
    const frame = new THREE.Group();
    station.group.add(frame);
    const plate = new THREE.Mesh(box, matMaterial);
    plate.scale.set(fw - .3, fh - .3, .16);
    plate.position.z = -.12;
    frame.add(plate);

    // Four lacquer rails and four gold fillets assemble around the photo.
    const makeBar = (material, x, y, sx, sy, sz, z) => {
      const bar = new THREE.Mesh(box, material);
      bar.position.set(x, y, z);
      bar.scale.set(sx, sy, sz);
      frame.add(bar);
      return { mesh: bar, x, y, sx, sy };
    };
    const rails = [
      makeBar(frameMaterial, 0, fh / 2 - .11, fw, .22, .3, 0),
      makeBar(frameMaterial, 0, -fh / 2 + .11, fw, .22, .3, 0),
      makeBar(frameMaterial, -fw / 2 + .11, 0, .22, fh, .3, 0),
      makeBar(frameMaterial, fw / 2 - .11, 0, .22, fh, .3, 0),
    ];
    const fillets = [
      makeBar(goldMaterial, 0, ph / 2 + .06, pw + .18, .05, .06, .03),
      makeBar(goldMaterial, 0, -ph / 2 - .06, pw + .18, .05, .06, .03),
      makeBar(goldMaterial, -pw / 2 - .06, 0, .05, ph + .16, .06, .03),
      makeBar(goldMaterial, pw / 2 + .06, 0, .05, ph + .16, .06, .03),
    ];
    // Corners and ropes are small details that cost a phone real draw calls.
    const corners = lite ? [] : [[-1, 1], [1, 1], [-1, -1], [1, -1]].map(([sx, sy]) => {
      const corner = new THREE.Mesh(box, goldMaterial);
      corner.position.set(sx * (fw / 2 - .11), sy * (fh / 2 - .11), .17);
      corner.scale.set(.36, .36, .05);
      frame.add(corner);
      return corner;
    });
    const ropes = [];
    if (!lite) {
      for (const sx of [-1, 1]) {
        const rope = new THREE.Mesh(box, woodMaterial);
        rope.scale.set(.05, HALL.h, .05);
        rope.position.set(sx * (fw / 2 - .5), fh / 2 + HALL.h / 2, -.02);
        frame.add(rope);
        ropes.push(rope);
      }
    }

    const uniforms = {
      map: { value: placeholder }, loaded: { value: 0 }, reveal: { value: 0 }, exitT: { value: 0 },
      modeIn: { value: photo.photoIndex % 4 }, modeOut: { value: station.modeOut }, time: { value: 0 },
      aspect: { value: aspect }, reflectAmount: { value: 0 }, hover: { value: 0 },
      hazeDensity: { value: scene.fog.density }, hazeColor: { value: hazeColor },
    };
    const picture = new THREE.Mesh(new THREE.PlaneGeometry(pw, ph), new THREE.ShaderMaterial({
      vertexShader: PHOTO_VERT, fragmentShader: PHOTO_FRAG, uniforms, transparent: true,
    }));
    picture.position.z = .05;
    frame.add(picture);

    let reflection = null;
    if (!lite) {
      const reflectionUniforms = { ...uniforms, reflectAmount: { value: .3 } };
      reflection = new THREE.Mesh(new THREE.PlaneGeometry(pw * 1.04, ph * 1.05), new THREE.ShaderMaterial({
        vertexShader: PHOTO_VERT, fragmentShader: PHOTO_FRAG, uniforms: reflectionUniforms, transparent: true, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2,
      }));
      reflection.rotation.x = -Math.PI / 2;
      station.group.add(reflection);
    }

    const item = {
      photo, station, frame, rails, fillets, corners, ropes, picture, reflection, uniforms,
      aspect, pw, ph, fw, fh, homeSlot: slot, slot, from: slot, swapT: 1, hoverT: 0,
      thumbState: 0, fullState: 0, loadedLevel: -1,
    };
    picture.userData.item = item;
    return item;
  }

  stations.forEach(station => {
    const group = new THREE.Group();
    group.position.copy(station.pos);
    group.quaternion.copy(station.quat);
    group.visible = false;
    scene.add(group);
    station.group = group;

    const doorW = HALL.w / 6 - .05;
    station.doors = [-1, 1].map(side => {
      const door = new THREE.Mesh(box, shojiMaterial);
      door.scale.set(doorW - .06, HALL.h * .74 - .1, .08);
      door.position.set(side * doorW / 2, HALL.h * .37, -.02);
      group.add(door);
      return { mesh: door, side, width: doorW };
    });

    station.leaves = [];
    if (station.outKind === 'fall') {
      [-1, 1].forEach(side => {
        const hinge = new THREE.Group();
        hinge.position.set(side * (HALL.w / 2 + .6), 0, 4);
        const leaf = new THREE.Mesh(box, plankMaterial);
        leaf.scale.set(HALL.w / 2 + .6, .3, HALL.d - 4);
        leaf.position.set(-side * (HALL.w / 2 + .6) / 2, -.15, (HALL.d - 4) / 2);
        hinge.add(leaf);
        for (let m = 0; m < 3; m++) {
          const mat = new THREE.Mesh(box, tatamiMaterial);
          mat.scale.set(HALL.w / 2 - .4, .02, (HALL.d - 4) / 3 - .03);
          mat.position.set(-side * (HALL.w / 2 + .6) / 2, .012, (m + .5) * (HALL.d - 4) / 3);
          hinge.add(mat);
        }
        group.add(hinge);
        station.leaves.push({ hinge, side });
      });
    }

    station.items = station.photos.map((photo, slot) => buildFramedPhoto(station, photo, slot));
    Object.assign(station, { restPos: v3(), heroLocal: v3() });
  });

  const centreItem = station => station.items.find(item => item.slot === 0);

  // Thumbs first, then full size for what's in view, so nothing ever arrives soft.
  function setPhotoTexture(item, src, level) {
    textureLoader.load(src, texture => {
      if (abort.signal.aborted || level <= item.loadedLevel || (level === 0 && item.thumbState === 0)) return texture.dispose();
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = lite ? 2 : renderer.capabilities.getMaxAnisotropy();
      texture.generateMipmaps = true;
      texture.minFilter = THREE.LinearMipmapLinearFilter;
      const old = item.uniforms.map.value;
      item.uniforms.map.value = texture;
      item.uniforms.loaded.value = 1;
      item.loadedLevel = level;
      if (old !== placeholder) old.dispose();
    });
  }
  function loadFull(item) {
    if (item.fullState) return;
    item.fullState = 1;
    setPhotoTexture(item, item.photo.src, 1);
  }
  function loadAround(index) {
    stations.forEach(station => {
      const distance = Math.abs(station.index - index);
      station.items.forEach(item => {
        if (distance <= 1 && !item.thumbState) { item.thumbState = 1; setPhotoTexture(item, item.photo.thumbnail, 0); }
        // A phone's screen is well served by the 640px thumbnail until a photo is enlarged.
        if (!lite && distance === 0) loadFull(item);
        // Phones keep only nearby rooms in memory; the rest reload when they come back into range.
        if (lite && distance > 1 && item.thumbState) {
          const old = item.uniforms.map.value;
          item.uniforms.map.value = placeholder;
          item.uniforms.loaded.value = 0;
          item.thumbState = item.fullState = 0;
          item.loadedLevel = -1;
          if (old !== placeholder) old.dispose();
        }
      });
    });
  }

  /* ----- Zenitsu ----- */

  const CELL_ASPECT = 410 / 212;
  const heroHeight = 2.3;
  const heroPlaneH = heroHeight * 295 / 275;
  const heroGeometry = new THREE.PlaneGeometry(heroPlaneH * CELL_ASPECT, heroPlaneH);
  heroGeometry.translate((.5 - 260 / 570) * heroPlaneH * CELL_ASPECT, heroPlaneH * (.5 - 5 / 295), 0);
  const heroMaterial = new THREE.MeshBasicMaterial({ map: spriteSet.idle, transparent: true, alphaTest: .35, side: THREE.DoubleSide, toneMapped: false, fog: false, color: new THREE.Color(1.03, .98, .92) });
  const hero = new THREE.Mesh(heroGeometry, heroMaterial);
  hero.renderOrder = 5;
  hero.frustumCulled = false;
  scene.add(hero);
  let heroSheet = 'idle', heroFacing = 1, idleClock = 0, heroSpecial = null;

  function heroFrame(name, index) {
    const sprite = SPRITES[name];
    const texture = spriteSet[name];
    if (heroSheet !== name) {
      heroMaterial.map = texture;
      heroSheet = name;
    }
    const i = clamp(Math.floor(index), 0, sprite.frames - 1);
    texture.offset.set((i % sprite.cols) / sprite.cols, 1 - (Math.floor(i / sprite.cols) + 1) / sprite.rows);
  }

  // Lightning: a pool of ribbons whose shape is regenerated whenever one is struck.
  const boltMaterial = new THREE.MeshBasicMaterial({ color: new THREE.Color(9, 7.2, 3), transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, toneMapped: false, fog: false });
  const boltSegments = 34;
  const bolts = Array.from({ length: 8 }, () => {
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array((boltSegments + 1) * 2 * 3), 3));
    const index = [];
    for (let i = 0; i < boltSegments; i++) { const a = i * 2; index.push(a, a + 1, a + 2, a + 1, a + 3, a + 2); }
    geometry.setIndex(index);
    const material = boltMaterial.clone();
    const mesh = new THREE.Mesh(geometry, material);
    mesh.visible = false;
    mesh.frustumCulled = false;
    scene.add(mesh);
    return { mesh, life: 0, max: 1, material };
  });
  let boltCursor = 0;
  const tempA = v3(), tempB = v3(), tempC = v3(), tempD = v3(), tempE = v3();
  const boltFrom = v3(), boltDir = v3(), boltSide = v3(), boltLift = v3(), boltPoint = v3();

  function strikeBolt(start, end, width = .14, life = .24) {
    const bolt = bolts[boltCursor++ % bolts.length];
    const positions = bolt.mesh.geometry.attributes.position;
    const from = boltFrom.copy(start);
    const dir = boltDir.copy(end).sub(start);
    const length = dir.length() || 1;
    const side = boltSide.copy(dir).cross(boltPoint.copy(camera.position).sub(from)).normalize();
    const lift = boltLift.copy(side).cross(dir).normalize();
    for (let i = 0; i <= boltSegments; i++) {
      const t = i / boltSegments;
      const envelope = Math.sin(Math.PI * t);
      const jitterA = (Math.random() - .5) * length * .07 * envelope;
      const jitterB = (Math.random() - .5) * length * .05 * envelope;
      const w = width * (.45 + Math.random() * .55) * (.3 + envelope * .7);
      boltPoint.copy(from).addScaledVector(dir, t).addScaledVector(side, jitterA).addScaledVector(lift, jitterB);
      positions.setXYZ(i * 2, boltPoint.x + side.x * w, boltPoint.y + side.y * w, boltPoint.z + side.z * w);
      positions.setXYZ(i * 2 + 1, boltPoint.x - side.x * w, boltPoint.y - side.y * w, boltPoint.z - side.z * w);
    }
    positions.needsUpdate = true;
    bolt.mesh.visible = true;
    bolt.life = bolt.max = life;
  }

  // Embers drifting through whatever the camera is looking at.
  const EMBERS = lite ? 110 : 620;
  const emberData = new Float32Array(EMBERS * 3);
  const emberSeed = new Float32Array(EMBERS);
  for (let i = 0; i < EMBERS; i++) {
    emberData[i * 3] = Math.random() * 44 - 22;
    emberData[i * 3 + 1] = Math.random() * 44 - 22;
    emberData[i * 3 + 2] = Math.random() * 44 - 22;
    emberSeed[i] = Math.random();
  }
  const emberGeometry = new THREE.BufferGeometry()
    .setAttribute('position', new THREE.BufferAttribute(emberData, 3))
    .setAttribute('seed', new THREE.BufferAttribute(emberSeed, 1));
  const emberUniforms = { time: { value: 0 }, origin: { value: v3() }, burst: { value: 0 }, map: { value: glowMap }, pixel: { value: 1 } };
  const embers = new THREE.Points(emberGeometry, new THREE.ShaderMaterial({
    uniforms: emberUniforms, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: /* glsl */`
      attribute float seed; uniform float time, burst, pixel; uniform vec3 origin; varying float vLife;
      void main(){
        vec3 p = position;
        p.y += time * (.5 + seed * 1.4);
        p.x += sin(time * .6 + seed * 40.) * 1.5 + time * .16;
        p.z += cos(time * .5 + seed * 22.) * 1.5;
        p = mod(p - origin + 22., 44.) - 22. + origin;
        vLife = .35 + .65 * abs(sin(time * (1. + seed * 2.) + seed * 19.));
        vec4 mv = viewMatrix * vec4(p, 1.);
        gl_Position = projectionMatrix * mv;
        gl_PointSize = min(70., pixel * (10. + seed * 26.) * (1. + burst * 1.4) / max(.5, -mv.z));
      }`,
    fragmentShader: /* glsl */`
      uniform sampler2D map; uniform float burst; varying float vLife;
      void main(){ float a = texture2D(map, gl_PointCoord).a; gl_FragColor = vec4(vec3(3., 1.35, .42) * (1. + burst * 1.3), a * vLife * .75); }`,
  }));
  embers.frustumCulled = false;
  scene.add(embers);

  // Ground shockwave for hard landings.
  const ringMaterial = new THREE.MeshBasicMaterial({ map: glowMap, color: new THREE.Color(5, 3.2, 1.3), transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false, fog: false });
  const ring = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), ringMaterial);
  ring.rotation.x = -Math.PI / 2;
  ring.visible = false;
  let ringLife = 0;

  /* ----- layout that depends on the screen ----- */

  // Where the three photographs hang. Slot 0 is the large one.
  const LANDSCAPE_SLOTS = [
    { x: 0, y: 3.55, z: .75, w: 6.6, h: 5.7, rotY: 0 },
    { x: -5.5, y: 4.6, z: 1.05, w: 3.9, h: 3.5, rotY: .24 },
    { x: 5.5, y: 4.6, z: 1.05, w: 3.9, h: 3.5, rotY: -.24 },
  ];
  const PORTRAIT_SLOTS = [
    { x: 0, y: 6.25, z: .75, w: 6.5, h: 5.5, rotY: 0 },
    { x: -1.7, y: 2.2, z: 1, w: 3.15, h: 2.25, rotY: .1 },
    { x: 1.7, y: 2.2, z: 1, w: 3.15, h: 2.25, rotY: -.1 },
  ];
  let slots = LANDSCAPE_SLOTS;
  const slotScale = (item, slot) => Math.min(slot.w / item.fw, slot.h / item.fh);
  let viewW = 1, viewH = 1, aspectRatio = 1;
  function layout() {
    viewW = root.clientWidth;
    viewH = root.clientHeight;
    if (!viewW || !viewH) { viewW = viewW || 1; viewH = viewH || 1; }
    aspectRatio = viewW / viewH;
    camera.aspect = aspectRatio;
    camera.fov = aspectRatio < 1 ? 50 : 38;
    slots = aspectRatio < 1 ? PORTRAIT_SLOTS : LANDSCAPE_SLOTS;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(pixelRatio);
    renderer.setSize(viewW, viewH, false);
    const pxW = Math.round(viewW * pixelRatio), pxH = Math.round(viewH * pixelRatio);
    renderTarget.setSize(pxW, pxH);
    const bloomShift = lite ? 3 : 2;
    bloomTargets[0].setSize(pxW >> bloomShift, pxH >> bloomShift);
    bloomTargets[1].setSize(pxW >> bloomShift, pxH >> bloomShift);
    if (!lite) {
      bloomTargets[2].setSize(pxW >> 4, pxH >> 4);
      bloomTargets[3].setSize(pxW >> 4, pxH >> 4);
    }
    emberUniforms.pixel.value = pixelRatio * Math.min(viewH, 1100) / 100;
    spacer.style.height = `${viewH + (N - 1) * viewH * 1.1}px`;

    const tanV = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const portrait = aspectRatio < 1;
    // Fit the whole arrangement, not one photo, so swapping never moves the camera.
    const contentW = portrait ? 6.75 : 15;
    const contentH = portrait ? 8.2 : 6.5;
    const distance = Math.max(
      (contentH / (portrait ? .72 : .84)) / (2 * tanV),
      (contentW / .95) / (2 * tanV * aspectRatio),
    );
    const spanV = 2 * distance * tanV;
    const lookY = portrait ? 5.15 - spanV * .05 : Math.max(Math.min(3.2, spanV / 2 - .32), 6.65 - spanV / 2);
    stations.forEach(station => {
      station.restLocal = v3(0, lookY, distance + .9);
      station.restPos.copy(station.restLocal).applyQuaternion(station.quat).add(station.pos);
      station.heroLocal.set(portrait ? 2.3 : Math.min(4.15, distance * tanV * aspectRatio - 2.6), 0, portrait ? 3.4 : 2.6);
    });
    stations.forEach(station => station.items.forEach(item => { item.swapT = 1; item.from = item.slot; }));
  }

  // Where the camera goes to show one photograph almost fullscreen.
  function inspectPose(item, out) {
    const tanV = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const slot = slots[0];
    const scale = slotScale(item, slot);
    const fit = Math.max((item.fh * scale * 1.05) / (2 * tanV), (item.fw * scale * 1.05) / (2 * tanV * aspectRatio));
    return out.set(slot.x, slot.y, slot.z + fit).applyQuaternion(item.station.quat).add(item.station.pos);
  }

  /* ----- the camera's journey ----- */

  const bezierTemp = [v3(), v3(), v3(), v3()];
  function bezier(a, b, c, d, t, out) {
    const u = 1 - t;
    return out.copy(a).multiplyScalar(u * u * u)
      .addScaledVector(b, 3 * u * u * t)
      .addScaledVector(c, 3 * u * t * t)
      .addScaledVector(d, t * t * t);
  }

  function segmentHandles(from, to) {
    const [a, b, c, d] = bezierTemp;
    a.copy(from.restPos);
    d.copy(to.restPos);
    const reach = a.distanceTo(d);
    const forward = tempA.set(0, 0, -1).applyQuaternion(from.quat);
    const forwardTo = tempB.set(0, 0, -1).applyQuaternion(to.quat);
    if (from.outKind === 'turn') {
      b.copy(a).add(tempC.set(from.side, 0, 0).applyQuaternion(from.quat).multiplyScalar(reach * .42));
      c.copy(d).addScaledVector(forwardTo, -reach * .34);
    } else if (from.outKind === 'fall') {
      b.copy(a).add(tempC.set(0, -1, 0).applyQuaternion(from.quat).multiplyScalar(reach * .7));
      c.copy(d).addScaledVector(forwardTo, -reach * .42);
    } else {
      b.copy(a).addScaledVector(forward, reach * .46);
      c.copy(d).addScaledVector(forwardTo, -reach * .4);
    }
    return bezierTemp;
  }

  const lookEuler = new THREE.Euler();
  const lookQuat = new THREE.Quaternion();
  const camPos = v3();
  const camQuat = new THREE.Quaternion();

  // Timings within one step of the scroll (s from 0 to 1).
  const stepExit = s => smooth(.08, .3, s);
  const stepDoors = s => smooth(.2, .38, s);
  const stepTravel = s => smoother(.28, .84, s);
  const stepReveal = s => smooth(.76, .985, s);

  function journey(p) {
    const seg = Math.min(Math.floor(p), N - 2);
    const s = clamp(p - seg);
    const from = stations[seg], to = stations[seg + 1];
    const travel = N > 1 ? stepTravel(s) : 0;
    const [a, b, c, d] = segmentHandles(from, to);
    bezier(a, b, c, d, travel, camPos);
    camQuat.copy(from.quat).slerp(to.quat, smoother(.08, .92, travel));
    const swing = Math.sin(Math.PI * travel);
    if (from.outKind === 'fall') {
      lookEuler.set(-swing * 1.25, 0, swing * from.side * .26);
    } else if (from.outKind === 'turn') {
      lookEuler.set(0, 0, swing * from.side * -.2);
    } else if (from.outKind === 'barrel') {
      lookEuler.set(swing * .12, swing * from.side * -.16, 0);
    } else {
      lookEuler.set(swing * -.05, swing * from.side * -.2, swing * from.side * .12);
    }
    camQuat.multiply(lookQuat.setFromEuler(lookEuler));
    return { seg, s, travel, from, to };
  }

  /* ----- opening ----- */

  const introStart = v3(), introCtl1 = v3(), introCtl2 = v3();
  function introCamera(t) {
    const first = stations[0];
    const local = (x, y, z, out) => out.set(x, y, z).applyQuaternion(first.quat).add(first.pos);
    local(0, first.restLocal.y + 210, first.restLocal.z + 26, introStart);
    local(0, first.restLocal.y + 42, first.restLocal.z + 26, introCtl1);
    local(0, first.restLocal.y, first.restLocal.z + 26, introCtl2);
    // Slow, even drift while he sleeps; the rest of the distance goes in one rush at the strike.
    const eased = t < .64 ? t / .64 * .62 : .62 + smoother(.64, .86, t) * .38;
    bezier(introStart, introCtl1, introCtl2, first.restPos, eased, camPos);
    const pitch = -.62 * (1 - smoother(.7, .9, t));
    camQuat.copy(first.quat).multiply(lookQuat.setFromEuler(lookEuler.set(pitch, 0, 0)));
  }

  /* ----- state ----- */

  let scrollTarget = 0, scrollSmooth = 0;
  let intro = { t: -1, clock: 0, done: false, cut: false };
  let elapsed = 0, lastFrame = performance.now(), rafId = 0, closing = 0;
  let flash = 0, shake = 0, prevCam = v3(), speedSmooth = 0;
  let inspect = 0, inspectTarget = 0, activeIndex = -1, activeRoom = -1, snapTimer = 0;
  let pointerX = 0, pointerY = 0, pointerSmoothX = 0, pointerSmoothY = 0, hovering = null;
  let lastBoltAt = 0;
  const firedEvents = new Set();
  const raycaster = new THREE.Raycaster();

  function stepHeight() { return Math.max(1, scroller.scrollHeight - scroller.clientHeight) / Math.max(1, N - 1); }
  let autoScroll = null, lastScrollTop = 0, scrollDirection = 1, touching = false;
  function glideTo(index) {
    const target = clamp(index, 0, N - 1) * stepHeight();
    const from = scroller.scrollTop;
    const steps = Math.abs(target - from) / stepHeight();
    if (steps < .002) return;
    autoScroll = { from, target, t: 0, duration: clamp(.55 + steps * 1.75, .55, 5) };
  }
  function goTo(index) {
    inspectTarget = 0;
    glideTo(index);
  }

  function showCaption(item) {
    const photo = item.photo;
    countEl.textContent = String(photo.photoIndex + 1).padStart(2, '0');
    altEl.textContent = '';
    altEl.setAttribute('aria-label', photo.alt);
    photo.alt.split(' ').forEach((word, i) => {
      const outer = document.createElement('span');
      outer.className = 'castle-word';
      const inner = document.createElement('span');
      inner.textContent = word;
      inner.style.setProperty('--i', i);
      outer.append(inner);
      altEl.append(outer, ' ');
    });
    // Replay the word-by-word rise when the photo changes while it's already showing.
    if (caption.classList.contains('is-shown')) {
      caption.classList.remove('is-shown');
      void caption.offsetWidth;
      caption.classList.add('is-shown');
    }
    ticks.forEach((tick, i) => {
      tick.toggleAttribute('data-active', i === item.station.index);
      if (i === item.station.index) tick.setAttribute('aria-current', 'true'); else tick.removeAttribute('aria-current');
    });
    renderPicks(item.station);
  }

  // Keyboard and screen-reader route to the same interaction as clicking a frame.
  function renderPicks(station) {
    picks.textContent = '';
    station.items.forEach(item => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'castle-pick';
      const forward = item.slot === 0;
      button.textContent = forward ? 'Enlarge photo' : 'Bring photo forward';
      button.setAttribute('aria-label', `${forward ? (inspectTarget ? 'Reduce' : 'Enlarge') : 'Bring forward'}: ${item.photo.alt}`);
      button.addEventListener('click', () => (forward ? toggleInspect() : bringForward(item)));
      picks.append(button);
    });
  }

  function showRoom(room) {
    roomNumeral.textContent = ROOM_NUMERALS[room % ROOM_NUMERALS.length];
    roomText.textContent = `Room ${String(room + 1).padStart(2, '0')} / ${String(rooms).padStart(2, '0')}`;
  }

  /* ----- page-side opening: he dashes to the button and cuts the page open ----- */

  const triggerRect = trigger.getBoundingClientRect();
  const pet = document.querySelector('.zenitsu-sprite');
  const petRect = pet && !pet.closest('[hidden]') ? pet.getBoundingClientRect() : null;
  const pageCell = { w: 182, h: 94 };
  pageHero.style.width = `${pageCell.w}px`;
  pageHero.style.height = `${pageCell.h}px`;
  pageHero.style.backgroundImage = `url("${PAGE_SLEEP}")`;
  pageHero.style.backgroundSize = `${23 * pageCell.w}px ${pageCell.h}px`;
  const heroStart = { x: petRect ? petRect.left : -pageCell.w, y: petRect ? petRect.top : triggerRect.top };
  const heroEnd = { x: clamp(triggerRect.left - 70, 0, innerWidth - pageCell.w), y: clamp(triggerRect.bottom - pageCell.h + 2, 0, innerHeight - pageCell.h) };
  const cutCentre = { x: clamp(triggerRect.left + 40, 0, innerWidth), y: clamp(triggerRect.top + triggerRect.height / 2, 0, innerHeight) };
  const cutAngle = -.5;
  const cutU = { x: Math.cos(cutAngle), y: Math.sin(cutAngle) };
  const cutN = { x: -cutU.y, y: cutU.x };
  const cutReach = Math.hypot(innerWidth, innerHeight) * 1.1;
  const cutCore = q('.castle-cut-core'), cutGlow = q('.castle-cut-glow'), cutA = q('.castle-cut-a'), cutB = q('.castle-cut-b');

  function jaggedLine() {
    const points = [];
    const count = 26;
    for (let i = 0; i <= count; i++) {
      const t = i / count * 2 - 1;
      const off = (Math.random() - .5) * 26;
      points.push(`${(cutCentre.x + cutU.x * t * cutReach + cutN.x * off).toFixed(1)},${(cutCentre.y + cutU.y * t * cutReach + cutN.y * off).toFixed(1)}`);
    }
    return points.join(' ');
  }

  function setBand(halfWidth) {
    const corner = (u, n) => `${(cutCentre.x + cutU.x * u + cutN.x * n).toFixed(1)}px ${(cutCentre.y + cutU.y * u + cutN.y * n).toFixed(1)}px`;
    world.style.clipPath = `polygon(${corner(-cutReach, -halfWidth)},${corner(cutReach, -halfWidth)},${corner(cutReach, halfWidth)},${corner(-cutReach, halfWidth)})`;
    for (const [line, sign] of [[cutA, -1], [cutB, 1]]) {
      line.setAttribute('x1', cutCentre.x - cutU.x * cutReach + cutN.x * halfWidth * sign);
      line.setAttribute('y1', cutCentre.y - cutU.y * cutReach + cutN.y * halfWidth * sign);
      line.setAttribute('x2', cutCentre.x + cutU.x * cutReach + cutN.x * halfWidth * sign);
      line.setAttribute('y2', cutCentre.y + cutU.y * cutReach + cutN.y * halfWidth * sign);
    }
  }

  // One rising z, in screen space.
  let nextSnore = 0;
  function snore(x, y) {
    const z = document.createElement('i');
    z.className = 'castle-z';
    z.textContent = 'z';
    z.style.left = `${x}px`;
    z.style.top = `${y}px`;
    z.style.setProperty('--drift', `${(14 + Math.random() * 18).toFixed(0)}px`);
    root.append(z);
    setTimeout(() => z.remove(), 1700);
  }

  function updateCut(clock) {
    const dashT = smooth(0, .14, clock);
    const dropped = Math.max(0, clock - CUT_AT - .12);
    pageHero.style.transform = `translate3d(${lerp(heroStart.x, heroEnd.x, dashT)}px,${lerp(heroStart.y, heroEnd.y, dashT) + dropped * dropped * 2200}px,0)`;
    pageHero.style.backgroundPosition = `${-Math.min(22, Math.floor(smooth(.14, .72, clock) * 23)) * pageCell.w}px 0`;
    pageHero.style.opacity = clock > CUT_AT + .75 ? '0' : '1';
    if (clock > .62 && clock < CUT_AT + .1 && clock > nextSnore) {
      nextSnore = clock + .3;
      snore(heroEnd.x + pageCell.w * .34, heroEnd.y + pageCell.h * .35);
    }
    if (clock < CUT_AT) {
      world.style.clipPath = 'polygon(0 0,0 0,0 0)';
      return;
    }
    if (!intro.cut) {
      intro.cut = true;
      const jag = jaggedLine();
      cutCore.setAttribute('points', jag);
      cutGlow.setAttribute('points', jag);
      sound.crack(.6);
      sound.strum(1, .75);
      flashEl.style.opacity = '.75';
      trigger.style.visibility = 'hidden';
    }
    const after = clock - CUT_AT;
    flashEl.style.opacity = String(Math.max(0, .75 - after * 3.4));
    cutCore.style.opacity = String(clamp(1 - after * 3.4));
    cutGlow.style.opacity = String(clamp(1 - after * 2.6));
    const openT = smooth(.1, 1.02, after);
    const band = openT * openT * cutReach + after * 8;
    if (openT >= 1) {
      world.style.clipPath = 'none';
      cutSvg.style.opacity = '0';
    } else {
      setBand(band);
      cutSvg.style.opacity = '1';
    }
  }

  /* ----- per-frame update of one station's moving parts ----- */

  function updateStation(station, reveal, exitT, doorsOpen, leavesOpen, mouseX, mouseY) {
    station.doors.forEach(({ mesh, side, width }) => {
      mesh.position.x = side * (width / 2 + doorsOpen * (width - .1));
    });
    station.leaves.forEach(({ hinge, side }) => {
      hinge.rotation.z = side * leavesOpen * 1.45;
    });
    station.items.forEach(item => updateItem(station, item, reveal, exitT, mouseX, mouseY));
  }

  const SLOT_DELAY = [.18, 0, .09];     // side photos arrive first, the large one last
  function updateItem(station, item, stationReveal, stationExit, mouseX, mouseY) {
    const delay = SLOT_DELAY[item.homeSlot] || 0;
    const reveal = clamp((stationReveal - delay) / (1 - .18));
    const exitT = clamp((stationExit - delay * .6) / (1 - .108));
    item.uniforms.reveal.value = reveal;
    item.uniforms.exitT.value = exitT;
    item.uniforms.time.value = elapsed;

    const showFrame = reveal > .001 && exitT < .999;
    item.frame.visible = showFrame;
    if (item.reflection) item.reflection.visible = false;
    if (!showFrame) return;

    // Rails fly in from beyond the room and clamp shut; fillets draw along their length.
    const assemble = smoother(.0, .62, reveal);
    const away = (1 - assemble) * 5 + smoother(.15, 1, exitT) * 6.5;
    if (away > .001 || item.railsMoved) {
      item.railsMoved = away > .001;
      item.rails.forEach(({ mesh, x, y }, i) => {
        const sx = i < 2 ? (i ? -1 : 1) * .3 : (i === 2 ? -1 : 1);
        const sy = i < 2 ? (i === 0 ? 1 : -1) : .3;
        mesh.position.x = x + sx * away;
        mesh.position.y = y + sy * away;
        mesh.rotation.z = (1 - assemble) * (i % 2 ? .3 : -.3) + exitT * (i % 2 ? .5 : -.5);
      });
    }
    const draw = smoother(.3, .92, reveal) * (1 - smooth(0, .3, exitT));
    item.fillets.forEach(({ mesh, sx, sy }, i) => {
      mesh.scale.x = i < 2 ? Math.max(.001, sx * draw) : sx;
      mesh.scale.y = i < 2 ? sy : Math.max(.001, sy * draw);
    });
    item.corners.forEach((corner, i) => {
      const k = Math.max(.001, smoother(.65, 1, reveal) * (1 - smooth(0, .2, exitT)));
      corner.scale.set(.36 * k, .36 * k, .05);
      corner.rotation.z = (1 - k) * 2;
    });

    // Ropes would cross the large photo when frames are stacked, and look wrong mid-flight.
    const showRopes = aspectRatio >= 1 && item.swapT >= 1;
    item.ropes.forEach(rope => { rope.visible = showRopes; });

    // Sliding between slots: an arc toward the viewer with a half twist.
    if (item.swapT < 1) item.swapT = Math.min(1, item.swapT + frameDt / .62);
    const k = smoother(0, 1, item.swapT);
    const arc = Math.sin(Math.PI * k);
    const a = slots[item.from], b = slots[item.slot];
    const scale = lerp(slotScale(item, a), slotScale(item, b), k);
    const hoverAim = hovering === item ? 1 : 0;
    item.hoverT += (hoverAim - item.hoverT) * Math.min(1, frameDt * 10);
    const isActive = station.index === activeIndex ? 1 : 0;
    const lift = station.modeOut === 2 ? smoother(.05, 1, exitT) * 9 : 0;
    item.frame.position.set(
      lerp(a.x, b.x, k),
      lerp(a.y, b.y, k) + lift + item.hoverT * .06,
      lerp(a.z, b.z, k) + arc * (item.slot === 0 ? 2.6 : 1.1) + (1 - assemble) * -.8 + item.hoverT * .35,
    );
    item.frame.scale.setScalar(scale * (1 + item.hoverT * (item.slot === 0 ? .012 : .05)));
    item.frame.rotation.set(
      -mouseY * .03 * isActive,
      lerp(a.rotY, b.rotY, k) + mouseX * .045 * isActive + arc * (item.slot === 0 ? -.5 : .5) + (1 - assemble) * .4 * (item.homeSlot === 1 ? -1 : 1),
      (1 - assemble) * .06 + arc * .05,
    );
    item.uniforms.hover.value = item.hoverT;

    // Only the large photograph reflects in the floor.
    if (item.reflection && item.slot === 0 && item.swapT >= 1 && reveal > .4 && exitT < .4) {
      item.reflection.visible = true;
      item.reflection.scale.setScalar(scale);
      item.reflection.position.set(item.frame.position.x, .05, item.frame.position.z + item.ph * scale * .525 + .25);
    }
  }

  /* ----- Zenitsu in the world, driven by the same timeline ----- */

  const pointC = v3(), pointD = v3();
  const heroWorld = v3(), heroAhead = v3(), heroRestA = v3(), heroRestB = v3();
  const camForward = v3(), camUp = v3(), camRight = v3();

  function placeAhead(distance, down, right, out) {
    return out.copy(camera.position).addScaledVector(camForward, distance).addScaledVector(camUp, -down).addScaledVector(camRight, right);
  }

  function updateHero(state, dt) {
    const { seg, s, from, to, travel } = state;
    let roll = 0;
    const scale = 1;
    heroRestA.copy(from.heroLocal).applyQuaternion(from.quat).add(from.pos);
    heroRestB.copy(to.heroLocal).applyQuaternion(to.quat).add(to.pos);
    placeAhead(11, 2.1, 0, heroAhead);
    const faceFrame = -1;

    if (heroSpecial && (s < .06 || s > .96)) {
      const sp = heroSpecial;
      sp.t += dt;
      const sheet = SPRITES[sp.name];
      heroFrame(sp.name, Math.min(sheet.frames - 1, sp.t * sp.fps));
      heroWorld.copy(s < .5 ? heroRestA : heroRestB);
      heroFacing = faceFrame;
      if (sp.t * sp.fps >= sheet.frames) heroSpecial = null;
    } else if (s < .06) {
      idleClock += dt;
      if (elapsed > nextAntic) {
        nextAntic = elapsed + 7 + Math.random() * 7;
        heroSpecial = { name: Math.random() < .5 ? 'spin' : 'slash', t: 0, fps: 20 };
      }
      heroFrame('idle', (idleClock * 14) % SPRITES.idle.frames);
      heroWorld.copy(heroRestA);
      heroFacing = faceFrame;
    } else if (s < .28) {
      const a = smooth(.06, .26, s);
      const name = from.modeOut === 1 ? 'spin' : 'slash';
      heroFrame(name, a * (SPRITES[name].frames - 1));
      heroWorld.copy(heroRestA);
      const lungeX = from.modeOut === 0 ? smooth(.06, .14, s) * -2.2 : 0;
      heroWorld.add(tempA.set(lungeX, 0, .3).applyQuaternion(from.quat));
      heroFacing = faceFrame;
    } else if (s < .36) {
      const a = smooth(.28, .36, s);
      heroFrame('dash', a * 11);
      heroWorld.copy(heroRestA);
      heroFacing = 1;
    } else if (s < .86) {
      const inFlight = smooth(.36, .44, s);
      const landing = smooth(.76, .86, s);
      if (from.outKind === 'fall') {
        heroFrame('hit', (elapsed * 10) % SPRITES.hit.frames);
        roll = s * 34;
      } else {
        heroFrame('dash', 12 + (elapsed * 34) % 16);
      }
      heroWorld.copy(heroRestA).lerp(heroAhead, inFlight).lerp(heroRestB, landing);
      heroFacing = 1;
      if (!lite && elapsed - lastBoltAt > .055 && inFlight > .5 && landing < .5) {
        lastBoltAt = elapsed;
        placeAhead(5.5, 1.4, (Math.random() - .5) * 3, tempE);
        strikeBoltBehindHero(heroWorld, tempE);
      }
    } else if (s < .96) {
      heroFrame('dash', 31 + smooth(.86, .96, s) * 4);
      heroWorld.copy(heroRestB);
      heroFacing = faceFrame;
    } else {
      idleClock += dt;
      heroFrame('idle', (idleClock * 14) % SPRITES.idle.frames);
      heroWorld.copy(heroRestB);
      heroFacing = faceFrame;
    }

    hero.position.copy(heroWorld);
    hero.quaternion.copy(camera.quaternion).multiply(scratchQuat.setFromAxisAngle(AXIS_Z, roll));
    hero.scale.set(heroFacing * scale, scale, scale);

    // Last photo: he's spent. Plays once, stays down until clicked.
    if (seg === N - 2 && s > .985 && !heroSpecial && !heroSpent) {
      heroSpent = true;
      heroSpecial = null;
    }
  }
  let heroSpent = false, faintClock = 0, nextAntic = 9;

  function strikeBoltBehindHero(from, to) { strikeBolt(tempD.copy(from).addScaledVector(camUp, 1), to, .018, .1); }

  function fireOnce(key, action) {
    if (firedEvents.has(key)) return;
    firedEvents.add(key);
    action();
  }

  /* ----- main loop ----- */

  function castleFrame(now) {
    rafId = requestAnimationFrame(castleFrame);
    const dt = clamp((now - lastFrame) / 1000, 0, .05);
    const rawDt = (now - lastFrame) / 1000;
    lastFrame = now;
    elapsed += dt;
    frameDt = dt;
    trackPerformance(rawDt);

    if (closing) {
      closing += dt;
      const t = clamp(closing / .42);
      compositeMaterial.uniforms.fade.value = 1 - t;
      root.style.opacity = String(1 - smooth(.5, 1, t));
      if (t >= 1) return teardown();
    }

    let state;
    if (!intro.done) {
      intro.clock += dt;
      updateCut(intro.clock);
      const t = clamp((intro.clock - CUT_AT) / INTRO_SECONDS);
      intro.t = t;
      introCamera(t);
      camera.position.copy(camPos);
      camera.quaternion.copy(camQuat);
      camera.getWorldDirection(camForward);
      camUp.set(0, 1, 0).applyQuaternion(camera.quaternion);
      camRight.set(1, 0, 0).applyQuaternion(camera.quaternion);
      updateIntro(t, dt);
      if (t >= 1) finishIntro();
    } else {
      if (autoScroll) {
        autoScroll.t = Math.min(1, autoScroll.t + dt / autoScroll.duration);
        scroller.scrollTop = lerp(autoScroll.from, autoScroll.target, smoother(0, 1, autoScroll.t));
        if (autoScroll.t >= 1) autoScroll = null;
      }
      scrollTarget = scroller.scrollTop / stepHeight();
      scrollSmooth += (scrollTarget - scrollSmooth) * (1 - Math.exp(-dt * 6.5));
      if (Math.abs(scrollTarget - scrollSmooth) < .00015) scrollSmooth = scrollTarget;
      const p = clamp(scrollSmooth, 0, N - 1);
      state = journey(p);
      camera.position.copy(camPos);
      camera.quaternion.copy(camQuat);

      const here = state.s < .5 ? state.from : state.to;
      atRestNow = state.s < .06 || state.s > .96;
      if (here.index !== activeIndex) {
        activeIndex = here.index;
        hovering = null;
        inspectTarget = 0;
        showCaption(centreItem(here));
        loadAround(activeIndex);
        if (here.room !== activeRoom) { activeRoom = here.room; showRoom(here.room); }
      }

      inspect += (inspectTarget - inspect) * (1 - Math.exp(-dt * 7));
      if (inspect > .001 && atRestNow) {
        camera.position.lerp(inspectPose(centreItem(here), tempA), inspect);
      }
      // Nudge the scene with the pointer; the frame tilts toward it too.
      pointerSmoothX += (pointerX - pointerSmoothX) * (1 - Math.exp(-dt * 4));
      pointerSmoothY += (pointerY - pointerSmoothY) * (1 - Math.exp(-dt * 4));
      const settle = 1 - inspect * .8;
      const breathe = Math.sin(elapsed * .5) * .035;
      camera.position.add(tempA.set(pointerSmoothX * .3 * settle, -pointerSmoothY * .18 * settle + breathe, 0).applyQuaternion(camera.quaternion));
      camera.quaternion.multiply(lookQuat.setFromEuler(lookEuler.set(-pointerSmoothY * .012 * settle, -pointerSmoothX * .018 * settle, 0)));
      camera.getWorldDirection(camForward);
      camUp.set(0, 1, 0).applyQuaternion(camera.quaternion);
      camRight.set(1, 0, 0).applyQuaternion(camera.quaternion);

      // Doors, photographs, floors
      stations.forEach(station => {
        const near = station.index >= state.seg && station.index <= state.seg + 1;
        station.group.visible = near;
        if (!near) return;
        let reveal = 0, exitT = 0, doorsOpen = 0, leavesOpen = 0;
        if (station.index === state.seg) {
          reveal = 1;
          exitT = stepExit(state.s);
          if (station.outKind === 'through' || station.outKind === 'barrel') doorsOpen = stepDoors(state.s);
          if (station.outKind === 'fall') leavesOpen = smooth(.22, .34, state.s);
        } else if (station.index === state.seg + 1) {
          reveal = stepReveal(state.s);
        } else if (station.index < state.seg) {
          reveal = 1; exitT = 1;
        }
        updateStation(station, reveal, exitT, doorsOpen, leavesOpen, pointerSmoothX, pointerSmoothY);
      });

      // Sound and light cues fire once when the timeline crosses them, either way.
      const key = `${state.seg}:${state.s < .11 ? 0 : state.s < .3 ? 1 : state.s < .8 ? 2 : 3}`;
      if (key !== lastEventKey) {
        const movedForward = !lastEventKey || compareEvent(key, lastEventKey) > 0;
        lastEventKey = key;
        if (movedForward && state.s >= .11 && state.s < .3) {
          const fromStation = state.from;
          if (fromStation.modeOut === 0) {
            flash = Math.max(flash, .52); shake = .28;
            sound.crack(.42);
            tempB.copy(state.from.pos).add(tempC.set(-7.5, 1, 2).applyQuaternion(state.from.quat));
            tempE.copy(state.from.pos).add(tempC.set(7.5, 7.2, 2).applyQuaternion(state.from.quat));
            strikeBolt(tempB, tempE, .05, .3);
          } else if (fromStation.modeOut === 1) {
            flash = Math.max(flash, .1);
            emberUniforms.burst.value = 1;
          }
        }
        if (movedForward && state.s >= .8) {
          emberUniforms.burst.value = Math.max(emberUniforms.burst.value, .7);
          sound.accent(1.122, .36);
          shake = Math.max(shake, .12);
        }
      }

      updateHero(state, dt);
      if (heroSpent && state.seg === N - 2 && state.s > .985) {
        faintClock += dt;
        heroFrame('faint', Math.min(SPRITES.faint.frames - 1, faintClock * 15));
        // He falls backwards, so step him inward or he lands off-screen behind the buttons.
        hero.position.addScaledVector(camRight, -smooth(0, .5, faintClock) * 2.4);
      } else if (faintClock) {
        faintClock = 0;
        heroSpent = false;
      }
      updateOverlay(state);
    }

    // Shared effects
    shake = Math.max(0, shake - dt * 1.6);
    if (shake > .001) {
      const a = shake * shake * 1.7;
      camera.position.add(tempA.set((Math.random() - .5) * a, (Math.random() - .5) * a, 0).applyQuaternion(camera.quaternion));
    }
    flash = Math.max(0, flash - dt * 3.1);
    emberUniforms.burst.value = Math.max(0, emberUniforms.burst.value - dt * 1.3);

    const moved = camera.position.distanceTo(prevCam) / Math.max(dt, .001);
    prevCam.copy(camera.position);
    speedSmooth += (clamp(moved / 70) - speedSmooth) * (1 - Math.exp(-dt * 9));
    const sleeping = !intro.done && intro.t < .7;
    sound.wind(sleeping ? speedSmooth * .16 : speedSmooth);
    compositeMaterial.uniforms.speed.value = !sleeping && speedSmooth > .02 ? speedSmooth : 0;
    compositeMaterial.uniforms.flash.value = flash;
    compositeMaterial.uniforms.time.value = elapsed;
    skyUniforms.time.value = elapsed;
    skyUniforms.flash.value = flash;
    sky.position.copy(camera.position);
    emberUniforms.time.value = elapsed;
    emberUniforms.origin.value.copy(camera.position);

    // Warm rig follows whichever room the camera is really in.
    const lightStation = state ? (state.s < .5 ? state.from : state.to) : stations[0];
    roomLight.position.set(0, HALL.h - 1.2, HALL.d * .55).applyQuaternion(lightStation.quat).add(lightStation.pos);
    frameLight.position.set(0, 5, 3.6).applyQuaternion(lightStation.quat).add(lightStation.pos);
    const flicker = 1 + Math.sin(elapsed * 7.3) * .03 + Math.sin(elapsed * 17.1) * .025;
    roomLight.intensity = 95 * flicker;
    lanternMaterial.color.setRGB(5.2 * flicker, 2.9 * flicker, 1.25 * flicker);
    shojiColor.setRGB(.8, .66, .54).multiplyScalar(1 + (flicker - 1) * .45);

    bolts.forEach(bolt => {
      if (bolt.life <= 0) { bolt.mesh.visible = false; return; }
      bolt.life -= dt;
      bolt.material.opacity = clamp(bolt.life / bolt.max);
    });

    if (ringLife > 0) {
      ringLife -= dt;
      const k = 1 - clamp(ringLife / .7);
      ring.scale.setScalar(2 + k * 34);
      ringMaterial.opacity = (1 - k) * .9;
      if (ringLife <= 0) ring.visible = false;
    }

    // Phones draw a resting room at half rate: nothing there needs 60fps and it saves battery.
    frameTick++;
    const swapping = state?.from.items.some(item => item.swapT < 1) || state?.to.items.some(item => item.swapT < 1);
    const quiet = lite && intro.done && atRestNow && !autoScroll && !swapping && !closing
      && Math.abs(scrollTarget - scrollSmooth) < .002 && Math.abs(inspect - inspectTarget) < .01 && flash <= 0;
    if (quiet && frameTick % 2) return;

    camera.updateMatrixWorld();
    renderer.setRenderTarget(renderTarget);
    renderer.render(scene, camera);
    if (bloomEnabled) {
      pickMaterial.uniforms.tex.value = renderTarget.texture;
      drawQuad(pickMaterial, bloomTargets[0]);
      blur(bloomTargets[0], bloomTargets[1], 1);
      if (!lite) {
        drawQuad(copyToSmall(), bloomTargets[2]);
        blur(bloomTargets[2], bloomTargets[3], 2.2);
      }
    }
    drawQuad(compositeMaterial, null);
  }

  let bloomEnabled = true, frameDt = 0, frameTick = 0, atRestNow = false;
  let lastEventKey = '';
  const compareEvent = (a, b) => {
    const [aSeg, aStage] = a.split(':').map(Number), [bSeg, bStage] = b.split(':').map(Number);
    return aSeg === bSeg ? aStage - bStage : aSeg - bSeg;
  };

  const blurTempDir = new THREE.Vector2();
  function blur(source, target, spread) {
    blurMaterial.uniforms.tex.value = source.texture;
    blurMaterial.uniforms.dir.value.copy(blurTempDir.set(spread / source.width, 0));
    drawQuad(blurMaterial, target);
    blurMaterial.uniforms.tex.value = target.texture;
    blurMaterial.uniforms.dir.value.copy(blurTempDir.set(0, spread / source.height));
    drawQuad(blurMaterial, source);
    blurMaterial.uniforms.tex.value = source.texture;
    blurMaterial.uniforms.dir.value.copy(blurTempDir.set(spread / source.width, spread / source.height));
    drawQuad(blurMaterial, target);
  }
  const copyMaterial = quadMaterial('uniform sampler2D tex; varying vec2 vUv; void main(){ gl_FragColor = texture2D(tex, vUv); }', { tex: { value: null } });
  function copyToSmall() {
    copyMaterial.uniforms.tex.value = bloomTargets[1].texture;
    return copyMaterial;
  }

  // Step quality down if this device can't hold the frame rate.
  let perfFrames = 0, perfTime = 0;
  function trackPerformance(rawDt) {
    if (rawDt > .25 || document.hidden) return;
    perfFrames++; perfTime += rawDt;
    if (perfFrames < 50) return;
    const average = perfTime / perfFrames;
    perfFrames = 0; perfTime = 0;
    if (average > .027) {
      if (pixelRatio > 1) { pixelRatio = Math.max(1, pixelRatio - (lite ? .125 : .4)); layout(); }
      else if (bloomEnabled) {
        bloomEnabled = false;
        compositeMaterial.uniforms.bloomGain.value = 0;
      }
    }
  }

  function updateIntro(t, dt) {
    const first = stations[0];
    stations.forEach(station => { station.group.visible = station.index <= 1; });
    const reveal = smooth(.83, 1, t);
    if (activeIndex !== 0) { activeIndex = 0; loadAround(0); showRoom(0); showCaption(centreItem(first)); activeRoom = 0; }
    updateStation(first, reveal, 0, 0, 0, 0, 0);

    // Gates burst open just ahead of the fall.
    gates.forEach((gate, i) => {
      const anchor = tempA.set(0, first.restLocal.y + gate.height, first.restLocal.z + 26).applyQuaternion(first.quat).add(first.pos);
      gate.group.position.copy(anchor);
      gate.group.quaternion.copy(first.quat);
      const distance = camera.position.distanceTo(anchor);
      const above = tempB.copy(camera.position).sub(anchor).dot(tempC.set(0, 1, 0).applyQuaternion(first.quat));
      const open = above < 58 ? smooth(58, 26, above) : 0;
      gate.leaves.forEach(({ mesh, side }) => { mesh.position.x = side * (7.5 + open * 15); });
      if (open > .02 && !gate.opened) {
        gate.opened = true;
      }
      gate.group.visible = distance < 240 && t < .85;
    });

    // He falls beside the visitor, then lands hard and cuts the first photo free.
    const firstHero = tempD.copy(first.heroLocal).applyQuaternion(first.quat).add(first.pos);
    let roll = 0;
    const heroAheadFall = placeAhead(9.5, .1, Math.sin(elapsed * .7) * .28, tempE);
    if (t < .64) {
      // Limp on his back, rocking slightly in the air. Nothing else moves him.
      heroFrame('faint', SPRITES.faint.frames - 1);
      roll = Math.sin(elapsed * .9) * .06;
      hero.position.copy(heroAheadFall);
      heroFacing = 1;
      if (elapsed > nextSnore) {
        nextSnore = elapsed + .7;
        tempC.copy(hero.position).project(camera);
        snore((tempC.x + 1) / 2 * viewW + 10, (1 - tempC.y) / 2 * viewH - 44);
      }
    } else if (t < .73) {
      // Still asleep, the lightning arrives first; then the stance.
      const a = smooth(.64, .73, t);
      heroFrame(a < .45 ? 'faint' : 'dash', a < .45 ? SPRITES.faint.frames - 1 : (a - .45) / .55 * 11);
      hero.position.copy(heroAheadFall);
      heroFacing = 1;
      fireOnce('wake', () => { sound.crack(.28); emberUniforms.burst.value = 1; });
      if (elapsed - lastBoltAt > (a < .45 ? .16 : .06)) {
        lastBoltAt = elapsed;
        const reach = 1.1 + a * 2.6;
        pointC.copy(hero.position).addScaledVector(camUp, 1).addScaledVector(camRight, (Math.random() - .5) * reach * 2).addScaledVector(camUp, (Math.random() - .5) * reach * 2);
        pointD.copy(hero.position).addScaledVector(camUp, 1);
        strikeBolt(pointD, pointC, .018 + a * .02, .12);
        flash = Math.max(flash, a * .1);
      }
    } else if (t < .78) {
      const a = smooth(.73, .78, t);
      heroFrame('dash', 12 + a * 14);
      hero.position.copy(heroAheadFall).lerp(firstHero, a * a);
      heroFacing = 1;
      fireOnce('strike', () => {
        flash = Math.max(flash, .55); shake = .2;
        sound.crack(.55);
        strikeBolt(heroAheadFall, firstHero, .06, .34);
      });
    } else {
      hero.position.copy(firstHero);
      heroFacing = -1;
      const a = smooth(.78, .97, t);
      heroFrame(t < .82 ? 'hit' : 'slash', t < .82 ? 3 : a * (SPRITES.slash.frames - 1));
      fireOnce('land', () => {
        flash = Math.max(flash, .36); shake = .55;
        sound.crack(.5); sound.strum(.75, .7);
        emberUniforms.burst.value = 1;
        ring.position.copy(firstHero).add(tempC.set(0, .08, 0).applyQuaternion(first.quat));
        ring.quaternion.copy(first.quat).multiply(scratchQuat.setFromAxisAngle(AXIS_X, -Math.PI / 2));
        ring.visible = true;
        scene.add(ring);
        ringLife = .7;
      });
      if (t > .84) fireOnce('reveal', () => {
        const top = tempB.copy(first.pos).add(tempC.set(-7.5, 7.2, 2).applyQuaternion(first.quat)).clone();
        const low = tempE.copy(first.pos).add(tempC.set(7.5, 1, 2).applyQuaternion(first.quat)).clone();
        strikeBolt(top, low, .05, .3);
        flash = Math.max(flash, .22);
      });
    }
    hero.quaternion.copy(camera.quaternion).multiply(scratchQuat.setFromAxisAngle(AXIS_Z, roll));
    hero.scale.set(heroFacing, 1, 1);
    title.classList.toggle('is-shown', t > .16 && t < .56);
    if (t > .06 && ui.hidden) { ui.hidden = false; closeButton.focus({ preventScroll: true }); }
    skipButton.hidden = t > .78;
  }

  function finishIntro() {
    intro.done = true;
    gates.forEach(gate => {
      scene.remove(gate.group);
    });
    world.style.clipPath = 'none';
    cutSvg.style.display = 'none';
    pageHero.style.display = 'none';
    flashEl.style.opacity = '0';
    title.classList.remove('is-shown');
    skipButton.hidden = true;
    root.classList.add('is-ready');
    scroller.style.overflowY = 'auto';
    scroller.focus({ preventScroll: true });
    showCaption(centreItem(stations[0]));
    caption.classList.add('is-shown');
    prevCam.copy(camera.position);
  }

  function updateOverlay(state) {
    const { s, seg, from, to } = state;
    const atRest = s < .07 || s > .93;
    caption.classList.toggle('is-shown', atRest);
    enlargeButton.toggleAttribute('data-off', !atRest);
    enlargeButton.textContent = inspectTarget ? 'Reduce' : 'Enlarge';
    hint.classList.toggle('is-shown', scrollSmooth < .02 && !inspectTarget);
    tip.classList.toggle('is-shown', !tipGone && scrollSmooth < .02);
    roomEl.classList.toggle('is-shown', atRest);
    const roomChange = from.room !== to.room;
    const cardT = roomChange ? smooth(.42, .56, s) * (1 - smooth(.74, .84, s)) : 0;
    if (roomChange && cardT > 0) {
      roomCard.querySelector('.castle-roomcard-numeral').textContent = ROOM_NUMERALS[to.room % ROOM_NUMERALS.length];
      roomCard.querySelector('.castle-roomcard-label').textContent = `Room ${String(to.room + 1).padStart(2, '0')}`;
    }
    roomCard.style.opacity = String(cardT);
    roomCard.style.transform = `translate(-50%,-50%) scale(${.84 + cardT * .16 + smooth(.56, .84, s) * .3})`;
    const atEnd = seg === N - 2 && s > .97;
    if (endCard.hidden === atEnd) endCard.hidden = !atEnd;
    q('.castle-next').disabled = atEnd;
    q('.castle-prev').disabled = seg === 0 && s < .03;
    rail.style.setProperty('--progress', String((seg + s) / Math.max(1, N - 1)));
  }

  /* ----- photographs in the current room ----- */

  const pointA = v3(), pointB = v3();
  function bringForward(item) {
    const station = item.station;
    if (item.slot === 0 || closing || !intro.done || station.index !== activeIndex) return;
    if (item.swapT < 1) return;
    const centre = centreItem(station);
    centre.from = 0; centre.slot = item.slot; centre.swapT = 0;
    item.from = item.slot; item.slot = 0; item.swapT = 0;
    inspectTarget = 0;
    dismissTip();
    item.frame.getWorldPosition(pointA);
    centre.frame.getWorldPosition(pointB);
    strikeBolt(pointA, pointB, .035, .22);
    flash = Math.max(flash, .08);
    emberUniforms.burst.value = Math.max(emberUniforms.burst.value, .5);
    sound.accent(item.homeSlot === 1 ? 1.122 : 1.26, .28);
    faintClock = 0;
    heroSpent = false;
    heroSpecial = { name: 'slash', t: 0, fps: 34 };
    showCaption(item);
    if (!lite) loadFull(item);
  }

  function cyclePhoto(direction) {
    const station = stations[activeIndex];
    if (!station || station.items.length < 2) return;
    const wanted = direction > 0 ? 2 : 1;
    const item = station.items.find(other => other.slot === wanted) || station.items.find(other => other.slot !== 0);
    bringForward(item);
    // After a swap focus would be lost with the rebuilt buttons.
  }

  function toggleInspect() {
    inspectTarget = inspectTarget ? 0 : 1;
    dismissTip();
    if (inspectTarget) loadFull(centreItem(stations[activeIndex]));
  }

  let tipGone = false;
  function dismissTip() {
    tipGone = true;
  }

  /* ----- input ----- */

  function setPointer(event) {
    pointerX = (event.clientX / viewW) * 2 - 1;
    pointerY = (event.clientY / viewH) * 2 - 1;
  }

  function pickTarget(event) {
    if (!intro.done || !atRestNow) return null;
    const station = stations[activeIndex];
    if (!station) return null;
    pickPoint.set((event.clientX / viewW) * 2 - 1, -(event.clientY / viewH) * 2 + 1);
    raycaster.setFromCamera(pickPoint, camera);
    const pictures = station.items.filter(item => item.frame.visible).map(item => item.picture);
    return raycaster.intersectObjects([hero, ...pictures], false)[0]?.object || null;
  }
  const pickPoint = new THREE.Vector2();

  scroller.addEventListener('pointermove', event => {
    if (event.pointerType === 'touch') return;
    setPointer(event);
    const hit = pickTarget(event);
    const item = hit?.userData.item || null;
    hovering = item;
    scroller.style.cursor = !hit ? '' : hit === hero || item.slot !== 0 ? 'pointer' : inspectTarget ? 'zoom-out' : 'zoom-in';
  }, listen);
  scroller.addEventListener('pointerleave', () => { hovering = null; }, listen);

  let pressAt = null;
  scroller.addEventListener('pointerdown', event => { pressAt = { x: event.clientX, y: event.clientY }; }, listen);
  scroller.addEventListener('click', event => {
    if (pressAt && Math.hypot(event.clientX - pressAt.x, event.clientY - pressAt.y) > 8) return;
    const hit = pickTarget(event);
    if (hit === hero) {
      faintClock = 0;
      heroSpent = false;
      heroSpecial = { name: Math.random() < .5 ? 'spin' : 'slash', t: 0, fps: 24 };
      emberUniforms.burst.value = 1;
      flash = Math.max(flash, .1);
      sound.crack(.25);
    } else if (hit) {
      const item = hit.userData.item;
      if (item.slot === 0) toggleInspect();
      else bringForward(item);
    } else if (inspectTarget) {
      toggleInspect();
    }
  }, listen);

  // Sideways swipe switches the photo; vertical stays native scrolling.
  let swipeFrom = null;
  scroller.addEventListener('touchstart', event => {
    const touch = event.changedTouches[0];
    swipeFrom = { x: touch.clientX, y: touch.clientY };
  }, { passive: true, signal: abort.signal });
  scroller.addEventListener('touchend', event => {
    if (!swipeFrom) return;
    const touch = event.changedTouches[0];
    const dx = touch.clientX - swipeFrom.x, dy = touch.clientY - swipeFrom.y;
    swipeFrom = null;
    if (Math.abs(dx) > 44 && Math.abs(dx) > Math.abs(dy) * 1.6 && atRestNow) cyclePhoto(dx < 0 ? 1 : -1);
  }, { passive: true, signal: abort.signal });

  scroller.addEventListener('scroll', () => {
    const top = scroller.scrollTop;
    if (Math.abs(top - lastScrollTop) > .5) scrollDirection = top > lastScrollTop ? 1 : -1;
    lastScrollTop = top;
    if (Math.abs(top / stepHeight() - scrollTarget) > .004) inspectTarget = 0;
    if (autoScroll) return;
    clearTimeout(snapTimer);
    snapTimer = setTimeout(snapToPhoto, 160);
  }, { passive: true, signal: abort.signal });
  const cancelGlide = () => { autoScroll = null; };
  scroller.addEventListener('wheel', cancelGlide, { passive: true, signal: abort.signal });
  scroller.addEventListener('touchstart', () => { touching = true; cancelGlide(); }, { passive: true, signal: abort.signal });
  const touchDone = () => { touching = false; clearTimeout(snapTimer); snapTimer = setTimeout(snapToPhoto, 160); };
  scroller.addEventListener('touchend', touchDone, { passive: true, signal: abort.signal });
  scroller.addEventListener('touchcancel', touchDone, { passive: true, signal: abort.signal });

  // A scroll gesture commits to the next photograph in that direction, so a visitor
  // is never left stranded mid-transition. Only a tiny nudge settles back.
  function snapToPhoto() {
    if (!intro.done || touching || closing) return;
    const p = scroller.scrollTop / stepHeight();
    const base = Math.floor(p), part = p - base;
    if (part < .004 || part > .996) return glideTo(Math.round(p));
    const threshold = .035;
    const target = scrollDirection > 0 ? (part > threshold ? base + 1 : base) : (part < 1 - threshold ? base : base + 1);
    glideTo(target);
  }

  q('.castle-next').addEventListener('click', () => goTo(Math.round(scrollTarget) + 1), listen);
  q('.castle-prev').addEventListener('click', () => goTo(Math.round(scrollTarget) - 1), listen);
  enlargeButton.addEventListener('click', toggleInspect, listen);
  soundButton.addEventListener('click', () => {
    sound.setMuted(!sound.muted);
    updateSoundLabel();
    try { localStorage.setItem('castle-muted', sound.muted ? '1' : '0'); } catch {}
  }, listen);
  closeButton.addEventListener('click', beginClose, listen);
  q('.castle-exit').addEventListener('click', beginClose, listen);
  skipButton.addEventListener('click', () => { intro.clock = CUT_AT + INTRO_SECONDS * .985; updateCut(9); }, listen);

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') { event.preventDefault(); beginClose(); return; }
    trapFocus(root, event);
    if (!intro.done) return;
    if (['BUTTON', 'A'].includes(document.activeElement?.tagName) && (event.key === ' ' || event.key === 'Enter')) return;
    const index = Math.round(scrollTarget);
    if (['ArrowDown', 'PageDown', ' '].includes(event.key)) { event.preventDefault(); goTo(index + 1); }
    else if (['ArrowUp', 'PageUp'].includes(event.key)) { event.preventDefault(); goTo(index - 1); }
    else if (event.key === 'Home') { event.preventDefault(); goTo(0); }
    else if (event.key === 'End') { event.preventDefault(); goTo(N - 1); }
    else if (event.key === 'Enter') { toggleInspect(); }
    else if (event.key === 'ArrowLeft') { event.preventDefault(); cyclePhoto(-1); }
    else if (event.key === 'ArrowRight') { event.preventDefault(); cyclePhoto(1); }
  }, listen);
  window.addEventListener('resize', layout, listen);
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) sound.ctx?.suspend?.();
    else { sound.ctx?.resume?.(); lastFrame = performance.now(); }
  }, listen);
  // Phones can reclaim the GPU under memory pressure. Fall back rather than leave a dead screen.
  canvas.addEventListener('webglcontextlost', event => {
    event.preventDefault();
    if (tornDown) return;
    teardown();
    openPlainGallery(photos, trigger);
  }, listen);

  function beginClose() {
    if (closing) return;
    closing = .0001;
  }

  let tornDown = false;
  function teardown() {
    if (tornDown) return;
    tornDown = true;
    cancelAnimationFrame(rafId);
    abort.abort();
    clearTimeout(snapTimer);
    sound.dispose();
    scene.traverse(object => {
      object.geometry?.dispose?.();
      if (object.material) {
        const materials = Array.isArray(object.material) ? object.material : [object.material];
        materials.forEach(material => {
          if (material.uniforms?.map?.value?.dispose) material.uniforms.map.value.dispose();
          material.dispose();
        });
      }
    });
    [woodMap, lacquerMap, plankMap, shojiMap, tatamiMap, glowMap, placeholder, ...Object.values(spriteSet)].forEach(texture => texture.dispose());
    renderTarget.dispose();
    bloomTargets.forEach(target => target.dispose());
    renderer.dispose();
    renderer.forceContextLoss();
    root.remove();
    unlock();
    trigger.style.visibility = '';
    trigger.focus({ preventScroll: true });
  }

  /* ----- go ----- */

  layout();
  loadAround(0);
  scroller.style.overflowY = 'hidden';
  lastFrame = performance.now();
  rafId = requestAnimationFrame(castleFrame);
}
