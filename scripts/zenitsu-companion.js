(() => {
  if (document.querySelector('.zenitsu-pet')) return;

  // Paths stay literal so optimize_site.py can append its cache-busting token.
  const SHEETS = {
    idle: { src: '/assets/personal/zenitsu/idle.webp', frames: 19, fps: 14 },
    run: { src: '/assets/personal/zenitsu/run.webp', frames: 9, fps: 16 },
    slash: { src: '/assets/personal/zenitsu/atk01.webp', frames: 19, fps: 18 },
    spin: { src: '/assets/personal/zenitsu/skl01.webp', frames: 21, fps: 18 },
    dash: { src: '/assets/personal/zenitsu/skl02.webp', frames: 36, fps: 26 },
    hit: { src: '/assets/personal/zenitsu/hit01.webp', frames: 7, fps: 14 },
    recoil: { src: '/assets/personal/zenitsu/hit02.webp', frames: 7, fps: 14 },
    faint: { src: '/assets/personal/zenitsu/die.webp', frames: 23, fps: 16 },
  };
  // Crop geometry from the sprite build, in captured pixels.
  const CROP_W = 570, CROP_H = 295, BODY_H = 275, FEET_X = 260, FEET_Y = 290;
  const GRAVITY = 2300, DASH_SPEED = 2800;
  const STORAGE_KEY = 'zenitsu-pet-hidden';

  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const random = (min, max) => min + Math.random() * (max - min);
  const pick = list => list[Math.floor(Math.random() * list.length)];
  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const lerp = (a, b, t) => a + (b - a) * t;
  const ease = t => 1 - (1 - clamp(t, 0, 1)) ** 3;
  const viewW = () => document.documentElement.clientWidth;
  const viewH = () => window.visualViewport?.height || innerHeight;
  // While a phone keyboard is up, the floor stays at the layout bottom, behind the keyboard,
  // so he never lands on the chat composer sitting just above it.
  let keyboardOpen = false;
  const floorY = () => (keyboardOpen ? innerHeight : viewH()) - 4;

  const layer = document.createElement('div');
  layer.className = 'zenitsu-pet';
  layer.setAttribute('aria-hidden', 'false');
  layer.innerHTML = `
    <div class="zenitsu-body">
      <div class="zenitsu-sprite"></div>
      <button type="button" class="zenitsu-hit" aria-label="Chat with Zenitsu, the site assistant"></button>
    </div>`;
  const launcher = document.createElement('div');
  launcher.className = 'zenitsu-launcher';
  launcher.innerHTML = `
    <button type="button" class="zenitsu-launcher-button" aria-label="Ask Zenitsu, the site's AI guide" aria-expanded="false" aria-controls="zenitsu-chat">
      <span class="zenitsu-disc"><img src="/assets/personal/zenitsu/avatar.webp" alt="" width="96" height="96" decoding="async"></span>
      <span class="zenitsu-launcher-label">Ask me</span>
    </button>`;

  const chatPanel = document.createElement('section');
  chatPanel.id = 'zenitsu-chat';
  chatPanel.className = 'zenitsu-chat';
  chatPanel.hidden = true;
  chatPanel.setAttribute('aria-label', 'Chat with Zenitsu, the site AI guide');
  chatPanel.innerHTML = `
    <header class="zenitsu-chat-head">
      <span class="zenitsu-disc zenitsu-disc-small"><img src="/assets/personal/zenitsu/avatar.webp" alt="" width="64" height="64" decoding="async"></span>
      <div class="zenitsu-chat-title"><strong>Zenitsu</strong><span>Isack's AI guide</span></div>
      <button type="button" class="zenitsu-icon-button zenitsu-chat-more" aria-label="More options" aria-expanded="false" aria-controls="zenitsu-options">
        <svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true"><g fill="currentColor"><circle cx="4" cy="10" r="1.5"/><circle cx="10" cy="10" r="1.5"/><circle cx="16" cy="10" r="1.5"/></g></svg>
      </button>
      <button type="button" class="zenitsu-icon-button zenitsu-chat-close" aria-label="Close chat"><svg viewBox="0 0 20 20" width="16" height="16" aria-hidden="true"><path d="M5 5l10 10M15 5L5 15" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg></button>
    </header>
    <div id="zenitsu-options" class="zenitsu-options" hidden>
      <button type="button" class="zenitsu-visibility"></button>
      <p>3D model: <a href="https://sketchfab.com/3d-models/agatsuma-zenitsu-8f877f1dc7b4475c831851c6defd4d7d" target="_blank" rel="noopener">Agatsuma Zenitsu by Witsanu Superball</a>, <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noopener">CC BY 4.0</a>. Animation frames rendered from the model.</p>
    </div>
    <div class="zenitsu-chat-log" role="log" aria-live="polite" tabindex="0"></div>
    <form class="zenitsu-chat-form">
      <input type="text" name="message" maxlength="500" autocomplete="off" enterkeyhint="send" placeholder="What do you want built?" aria-label="Your message">
      <button type="submit" class="zenitsu-send" aria-label="Send message">
        <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true"><path d="M10 15.5v-11M5.5 9L10 4.5 14.5 9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </button>
    </form>
    <p class="zenitsu-chat-note">AI can be wrong. Messages go to Z.ai, so please avoid private details.</p>`;

  const body = layer.querySelector('.zenitsu-body');
  const sprite = layer.querySelector('.zenitsu-sprite');
  const hitBox = layer.querySelector('.zenitsu-hit');
  const launcherButton = launcher.querySelector('.zenitsu-launcher-button');
  const launcherLabel = launcher.querySelector('.zenitsu-launcher-label');
  const moreButton = chatPanel.querySelector('.zenitsu-chat-more');
  const optionsPanel = chatPanel.querySelector('.zenitsu-options');
  const visibility = chatPanel.querySelector('.zenitsu-visibility');

  const pet = { x: 0, y: 0, vx: 0, vy: 0, dir: 1, rot: 0, pivotBody: false, surface: null, airborne: false };
  let scale = 0, cellW = 0, cellH = 0;
  let sheet = null, frame = -1;
  let behavior = null, lastTime = 0, rafId = 0;
  let hidden = false;
  try { hidden = localStorage.getItem(STORAGE_KEY) === '1'; } catch {}

  /* ---------- rendering ---------- */

  function measure() {
    const target = viewW() < 700 ? 66 : 88;
    scale = target / BODY_H;
    cellW = Math.round(CROP_W * scale);
    cellH = Math.round(CROP_H * scale);
    sprite.style.width = `${cellW}px`;
    sprite.style.height = `${cellH}px`;
    body.style.width = `${cellW}px`;
    body.style.height = `${cellH}px`;
    const feetX = Math.round(FEET_X * scale);
    const feetY = Math.round(FEET_Y * scale);
    body.style.setProperty('--feet-x', `${feetX}px`);
    body.style.setProperty('--feet-y', `${feetY}px`);
    body.style.setProperty('--body-h', `${target}px`);
    sheet = sheet && { ...sheet, applied: false };
    frame = -1;
  }

  function show(name, index) {
    const data = SHEETS[name];
    const key = name;
    const cols = data.cols || data.frames, rows = data.rows || 1;
    if (!sheet || sheet.name !== key || !sheet.applied) {
      sheet = { name: key, applied: true };
      sprite.style.backgroundImage = `url("${data.src}")`;
      sprite.style.backgroundSize = `${cols * cellW}px ${rows * cellH}px`;
      frame = -1;
    }
    if (index !== frame) {
      frame = index;
      sprite.style.backgroundPosition = `${-(index % cols) * cellW}px ${-Math.floor(index / cols) * cellH}px`;
    }
  }

  // Every style write invalidates style; while he stands still, nothing is written at all.
  const written = { move: '', origin: '', turn: '' };
  function draw() {
    const feetX = FEET_X * scale, feetY = FEET_Y * scale;
    const move = `translate3d(${(pet.x - feetX).toFixed(1)}px,${(pet.y - feetY).toFixed(1)}px,0)`;
    const origin = `${feetX}px ${pet.pivotBody ? feetY - BODY_H * scale * .45 : feetY}px`;
    const turn = `rotate(${pet.rot.toFixed(1)}deg) scaleX(${pet.dir})`;
    if (move !== written.move) body.style.transform = written.move = move;
    if (origin !== written.origin) sprite.style.transformOrigin = written.origin = origin;
    if (turn !== written.turn) sprite.style.transform = written.turn = turn;
  }

  /* ---------- effects ---------- */

  function effect(tag, className, ttl) {
    const node = document.createElement(tag);
    node.className = className;
    layer.append(node);
    setTimeout(() => node.remove(), ttl);
    return node;
  }

  function sparks(x, y, count = 8) {
    for (let i = 0; i < count; i++) {
      const spark = effect('i', 'zenitsu-spark', 520);
      const angle = random(0, Math.PI * 2), reach = random(20, 70);
      spark.style.left = `${x}px`;
      spark.style.top = `${y}px`;
      spark.style.setProperty('--dx', `${(Math.cos(angle) * reach).toFixed(0)}px`);
      spark.style.setProperty('--dy', `${(Math.sin(angle) * reach).toFixed(0)}px`);
      spark.style.setProperty('--turn', `${angle.toFixed(2)}rad`);
    }
  }

  function bolt(x1, y1, x2, y2) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('class', 'zenitsu-bolt');
    const length = Math.hypot(x2 - x1, y2 - y1) || 1;
    const nx = -(y2 - y1) / length, ny = (x2 - x1) / length;
    const steps = Math.max(3, Math.round(length / 70));
    let points = `${x1},${y1}`;
    for (let i = 1; i < steps; i++) {
      const offset = random(-22, 22), along = i / steps;
      points += ` ${(x1 + (x2 - x1) * along + nx * offset).toFixed(0)},${(y1 + (y2 - y1) * along + ny * offset).toFixed(0)}`;
    }
    points += ` ${x2},${y2}`;
    svg.innerHTML = `<polyline points="${points}" class="zenitsu-bolt-glow"/><polyline points="${points}" class="zenitsu-bolt-core"/>`;
    layer.append(svg);
    setTimeout(() => svg.remove(), 420);
  }

  function slashArc() {
    const arc = effect('i', 'zenitsu-arc', 300);
    arc.style.left = `${pet.x + pet.dir * 42 * (scale / .32)}px`;
    arc.style.top = `${pet.y - BODY_H * scale * .55}px`;
    arc.style.setProperty('--flip', pet.dir);
  }

  function snore() {
    const z = effect('i', 'zenitsu-z', 1500);
    z.textContent = 'z';
    z.style.left = `${pet.x + random(-8, 24)}px`;
    z.style.top = `${pet.y - 36}px`;
  }

  /* ---------- surfaces: the page's own headings and images ---------- */

  function surfaceBounds(surface) {
    if (!surface.el.isConnected) return null;
    if (!surface.range) {
      const rect = surface.el.getBoundingClientRect();
      return rect.width ? { left: rect.left, right: rect.right, top: rect.top } : null;
    }
    // Text: only the first line is walkable, since later lines can be wider.
    const rects = [...surface.range.getClientRects()].filter(rect => rect.width);
    if (!rects.length) return null;
    const top = Math.min(...rects.map(rect => rect.top));
    const line = rects.filter(rect => rect.top < top + rects[0].height * .5);
    return {
      left: Math.min(...line.map(rect => rect.left)),
      right: Math.max(...line.map(rect => rect.right)),
      top: top + surface.inset,
    };
  }

  function usable(bounds) {
    return bounds && bounds.top > 70 && bounds.top < floorY() - 40 && bounds.right > 0 && bounds.left < viewW();
  }

  function findSurfaces() {
    const found = [];
    const nodes = document.querySelectorAll('h1,h2,h3,img,picture,video,article,figure');
    for (const el of nodes) {
      if (found.length >= 40) break;
      if (el.closest('nav,header,.zenitsu-pet,.zenitsu-launcher,.zenitsu-chat')) continue;
      const box = el.getBoundingClientRect();
      if (box.bottom < 70 || box.top > viewH() || box.width < 100) continue;
      const isText = /^H[1-3]$/.test(el.tagName);
      let range = null, rect = box;
      if (isText) {
        range = document.createRange();
        range.selectNodeContents(el);
        rect = range.getBoundingClientRect();
      }
      const lineHeight = isText ? parseFloat(getComputedStyle(el).fontSize) || rect.height : 0;
      const surface = { el, range, inset: lineHeight * .12 };
      const bounds = surfaceBounds(surface);
      if (!usable(bounds) || bounds.right - bounds.left < 100) continue;
      if (getComputedStyle(el).visibility === 'hidden' || Number(getComputedStyle(el).opacity) < .2) continue;
      // Something covering the top edge means he'd be standing on nothing visible.
      const probeX = clamp((bounds.left + bounds.right) / 2, 1, viewW() - 1);
      const top = document.elementFromPoint(probeX, bounds.top + 6);
      if (!top || !(el.contains(top) || top.contains(el))) continue;
      found.push(surface);
    }
    return found;
  }

  function range() {
    const margin = 26;
    const bounds = pet.surface && surfaceBounds(pet.surface);
    const left = bounds ? Math.max(bounds.left + 8, margin) : margin;
    const right = bounds ? Math.min(bounds.right - 8, viewW() - margin) : viewW() - margin;
    return right > left ? [left, right] : [pet.x, pet.x];
  }

  /* ---------- moves: each is a generator advanced one frame at a time ---------- */

  function* play(name, { from = 0, to = SHEETS[name].frames - 1, fps = SHEETS[name].fps, seconds = 0 } = {}) {
    const length = to - from + 1;
    let time = 0;
    while (seconds ? time < seconds : time * fps < length) {
      show(name, from + (Math.floor(time * fps) % length));
      time += yield;
    }
  }

  function* idle(seconds = random(.5, 1.6)) {
    yield* play('idle', { seconds });
  }

  function* runTo(target, speed = random(210, 330)) {
    pet.dir = target >= pet.x ? 1 : -1;
    let time = 0;
    while (Math.abs(target - pet.x) > 4) {
      const dt = yield;
      time += dt;
      show('run', Math.floor(time * SHEETS.run.fps * (speed / 240)) % SHEETS.run.frames);
      const step = speed * dt;
      pet.x += Math.sign(target - pet.x) * Math.min(step, Math.abs(target - pet.x));
    }
  }

  function* roam() {
    const [left, right] = range();
    const reach = pet.surface ? right - left : Math.min(right - left, 520);
    const target = clamp(pet.x + (Math.random() < .5 ? -1 : 1) * random(reach * .35, reach), left, right);
    yield* runTo(target);
  }

  // Ballistic flight. Lands on `land` if he reaches it, otherwise falls to the floor.
  function* fly(land = null, spin = 0) {
    pet.surface = null;
    pet.airborne = true;
    pet.pivotBody = spin !== 0;
    let turned = 0;
    while (true) {
      const dt = yield;
      pet.vy += GRAVITY * dt;
      pet.x += pet.vx * dt;
      pet.y += pet.vy * dt;
      const width = viewW();
      if (pet.x < 16 || pet.x > width - 16) {
        pet.x = clamp(pet.x, 16, width - 16);
        pet.vx *= -.6;
        pet.dir = pet.vx >= 0 ? 1 : -1;
      }
      turned += spin * dt;
      pet.rot = turned;
      if (pet.vy < 0) show('run', 2);
      else show('hit', 3);
      if (pet.vy > 0) {
        const bounds = land && surfaceBounds(land);
        if (usable(bounds) && pet.y >= bounds.top && pet.y - pet.vy * dt <= bounds.top + 14
          && pet.x > bounds.left && pet.x < bounds.right) {
          pet.y = bounds.top;
          pet.surface = land;
          break;
        }
        if (pet.y >= floorY()) { pet.y = floorY(); break; }
      }
    }
    pet.airborne = false;
    pet.rot = 0;
    pet.pivotBody = false;
    pet.vx = pet.vy = 0;
    yield* play('recoil', { from: 2, to: 2, seconds: .08 });
  }

  // Solve the launch so the arc peaks above both ends and lands on the target.
  function launch(targetX, targetY) {
    const apex = Math.max(16, Math.min(pet.y, targetY) - random(60, 150));
    const up = Math.sqrt(2 * Math.max(pet.y - apex, 1) / GRAVITY);
    const down = Math.sqrt(2 * Math.max(targetY - apex, 1) / GRAVITY);
    pet.vy = -GRAVITY * up;
    pet.vx = (targetX - pet.x) / (up + down);
    pet.dir = targetX >= pet.x ? 1 : -1;
  }

  function* crouch() {
    yield* play('recoil', { from: 0, to: 2, fps: 24 });
  }

  function* jumpToSurface() {
    const options = findSurfaces().filter(option => option.el !== pet.surface?.el);
    if (!options.length) { yield* roam(); return; }
    const land = pick(options);
    const bounds = surfaceBounds(land);
    const targetX = random(Math.max(bounds.left + 10, 26), Math.min(bounds.right - 10, viewW() - 26));
    yield* crouch();
    launch(targetX, bounds.top);
    yield* fly(land, Math.random() < .35 ? pet.dir * 720 : 0);
  }

  function* jumpDown() {
    const [left, right] = range();
    yield* crouch();
    launch(clamp(pet.x + random(-200, 200), left - 60, right + 60), floorY());
    yield* fly(null, Math.random() < .5 ? pet.dir * 360 : 0);
  }

  function* flip() {
    yield* crouch();
    pet.vy = -random(760, 1050);
    pet.vx = pet.dir * random(60, 220);
    const land = pet.surface;
    yield* fly(land, pet.dir * pick([360, 720, 1080]));
  }

  // Straight-line blink with a lightning trail; the signature move.
  function* blink(x, y, land) {
    const startX = pet.x, startY = pet.y;
    const distance = Math.hypot(x - startX, y - startY);
    const duration = Math.max(distance / DASH_SPEED, .05);
    pet.surface = null;
    pet.airborne = true;
    pet.dir = x >= startX ? 1 : -1;
    pet.pivotBody = true;
    pet.rot = clamp(Math.atan2(y - startY, Math.abs(x - startX)) * 57.3, -50, 50) * pet.dir;
    sparks(startX, startY - 30, 6);
    let time = 0;
    while (time < duration) {
      const progress = time / duration;
      pet.x = startX + (x - startX) * progress;
      pet.y = startY + (y - startY) * progress;
      show('dash', 12 + (Math.floor(time * 60) % 16));
      time += yield;
    }
    pet.x = x; pet.y = y;
    pet.rot = 0;
    pet.pivotBody = false;
    pet.airborne = false;
    pet.surface = land;
    bolt(startX, startY - 34, x, y - 34);
    sparks(x, y - 30, 12);
  }

  function* thunder() {
    yield* play('dash', { from: 0, to: 11 });
    const hops = Math.round(random(2, 5));
    const surfaces = findSurfaces();
    for (let i = 0; i < hops; i++) {
      const land = surfaces.length && Math.random() < .45 ? pick(surfaces) : null;
      const bounds = land && surfaceBounds(land);
      if (land && !usable(bounds)) continue;
      const x = bounds
        ? random(Math.max(bounds.left + 10, 26), Math.min(bounds.right - 10, viewW() - 26))
        : random(26, viewW() - 26);
      yield* blink(x, bounds ? bounds.top : floorY(), land);
      yield* play('dash', { from: 28, to: 30, seconds: .07 });
    }
    if (pet.surface === null && pet.y < floorY()) yield* fly();
    yield* play('dash', { from: 31, to: 35 });
  }

  function* slash() {
    const name = 'slash';
    const lunge = pet.dir * 90;
    const [left, right] = range();
    const startX = pet.x;
    let time = 0, swung = false;
    while (time * SHEETS[name].fps < SHEETS[name].frames) {
      const index = Math.floor(time * SHEETS[name].fps);
      show(name, index);
      if (index >= 5 && index <= 9) {
        pet.x = clamp(startX + lunge * ((index - 5) / 4), left, right);
      }
      if (index >= 6 && !swung) { swung = true; slashArc(); sparks(pet.x + pet.dir * 40, pet.y - 40, 5); }
      time += yield;
    }
  }

  function* spin() {
    yield* play('spin', { to: 7 });
    sparks(pet.x, pet.y - 34, 10);
    yield* play('spin', { from: 8 });
  }

  function* wallRun() {
    const wall = pet.x > viewW() / 2 ? 1 : -1;
    const edge = wall > 0 ? viewW() - 8 : 8;
    yield* runTo(edge, 380);
    pet.dir = wall;
    pet.airborne = true;
    pet.rot = -90 * wall;
    const stop = viewH() * random(.22, .5);
    let time = 0;
    while (pet.y > stop) {
      const dt = yield;
      time += dt;
      pet.y -= 480 * dt;
      show('run', Math.floor(time * 24) % SHEETS.run.frames);
    }
    pet.rot = 0;
    pet.dir = -wall;
    pet.vx = -wall * random(360, 620);
    pet.vy = -random(260, 520);
    yield* fly(null, -wall * 720);
  }

  function* faint(seconds = random(2.5, 4.5)) {
    yield* play('faint');
    let time = 0, next = .2;
    while (time < seconds) {
      show('faint', SHEETS.faint.frames - 1);
      if (time > next) { snore(); next += .8; }
      time += yield;
    }
    yield* play('faint', { from: 0, to: 0, seconds: .06 });
  }

  function* startled() {
    sparks(pet.x, pet.y - 34, 8);
    yield* play(pick(['hit', 'recoil']));
  }

  // Hanging from the pointer until released.
  function* held() {
    pet.surface = null;
    pet.airborne = true;
    pet.pivotBody = true;
    let time = 0;
    while (true) {
      const dt = yield;
      time += dt;
      pet.x += (dragState.x - pet.x) * Math.min(1, dt * 22);
      pet.y += (dragState.y + BODY_H * scale * .8 - pet.y) * Math.min(1, dt * 22);
      pet.rot = clamp(dragState.vx * .03, -55, 55) + Math.sin(time * 7) * 6;
      show('hit', Math.floor(time * 10) % SHEETS.hit.frames);
    }
  }

  function* thrown(vx, vy) {
    pet.vx = clamp(vx, -2200, 2200);
    pet.vy = clamp(vy, -1800, 1800);
    pet.dir = pet.vx >= 0 ? 1 : -1;
    yield* fly(null, clamp(vx * .5, -900, 900));
    sparks(pet.x, pet.y - 8, 8);
    yield* play('recoil');
  }

  function* hopOnto(surface) {
    const bounds = surfaceBounds(surface);
    if (!bounds || bounds.top < 70) { yield* idle(.4); return; }
    yield* blink(clamp(bounds.right - 70, bounds.left + 20, bounds.right - 20), bounds.top, surface);
    yield* play('dash', { from: 31, to: 35 });
  }

  function* entrance() {
    pet.x = -60; pet.y = floorY(); pet.dir = 1;
    yield* blink(viewW() * random(.55, .8), floorY(), null);
    yield* play('dash', { from: 31, to: 35 });
    yield* slash();
  }

  function chooseMove() {
    const home = perch();
    if (home) {
      if (pet.surface !== home) return hopOnto(home);
      return chat.thinking ? roam() : idle(random(1.2, 2.4));
    }
    const grounded = !pet.surface;
    const moves = [
      [roam, 6], [idle, 3], [thunder, 3], [slash, 2], [spin, 2], [flip, 3],
      [jumpToSurface, grounded ? 5 : 3], [faint, .5],
    ];
    if (grounded) moves.push([wallRun, 2]);
    else moves.push([jumpDown, 3]);
    let roll = Math.random() * moves.reduce((sum, [, weight]) => sum + weight, 0);
    for (const [move, weight] of moves) {
      roll -= weight;
      if (roll <= 0) return move();
    }
    return roam();
  }

  // A move interrupted in mid-air drops him to the ground before the next one.
  function* afterLanding(generator) {
    pet.vx = pet.vy = 0;
    yield* fly();
    yield* generator;
  }

  function start(generator, settle = true) {
    const inAir = settle && !pet.surface && pet.y < floorY() - 2;
    pet.pivotBody = false;
    pet.rot = 0;
    pet.airborne = false;
    behavior = inAir ? afterLanding(generator) : generator;
    behavior.next();
  }

  function tick(time) {
    rafId = requestAnimationFrame(tick);
    const dt = clamp((time - lastTime) / 1000 || 0, 0, .05);
    lastTime = time;

    // His surface moves with the page, so he rides it and drops off if it leaves.
    if (pet.surface) {
      const bounds = surfaceBounds(pet.surface);
      if (usable(bounds)) {
        pet.y = bounds.top;
      } else {
        pet.surface = null;
        pet.vx = 0; pet.vy = 0;
        start(fly(), false);
      }
    } else if (!pet.airborne) {
      pet.y = floorY();
    }

    if (!behavior) start(chooseMove());
    if (behavior.next(dt).done) start(chooseMove());
    draw();
  }

  /* ---------- pointer: click for a move, drag to throw ---------- */

  const dragState = { active: false, id: null, x: 0, y: 0, vx: 0, vy: 0, lastT: 0, startX: 0, startY: 0, pressed: false };
  let clicks = [];

  function reactToClick() {
    if (motion.matches) return;
    const now = performance.now();
    clicks = clicks.filter(stamp => now - stamp < 2500);
    clicks.push(now);
    if (clicks.length >= 5) {
      clicks = [];
      start((function* () { yield* startled(); yield* faint(); })());
      return;
    }
    // First press opens the chat; once it's open he just shows off in place.
    if (!chat.open) { setChat(true); return; }
    const move = pick([slash, spin]);
    start((function* () { yield* startled(); yield* move(); })());
  }

  hitBox.addEventListener('pointerdown', event => {
    if (motion.matches || event.button) return;
    hitBox.setPointerCapture(event.pointerId);
    Object.assign(dragState, { pressed: true, id: event.pointerId, startX: event.clientX, startY: event.clientY, x: event.clientX, y: event.clientY, vx: 0, vy: 0, lastT: event.timeStamp });
  });

  hitBox.addEventListener('pointermove', event => {
    if (!dragState.pressed || event.pointerId !== dragState.id) return;
    if (!dragState.active && Math.hypot(event.clientX - dragState.startX, event.clientY - dragState.startY) > 8) {
      dragState.active = true;
      start(held(), false);
    }
    if (dragState.active) {
      const elapsed = Math.max(event.timeStamp - dragState.lastT, 1) / 1000;
      dragState.vx = dragState.vx * .6 + ((event.clientX - dragState.x) / elapsed) * .4;
      dragState.vy = dragState.vy * .6 + ((event.clientY - dragState.y) / elapsed) * .4;
      dragState.x = event.clientX;
      dragState.y = event.clientY;
      dragState.lastT = event.timeStamp;
    }
  });

  function release(event) {
    if (!dragState.pressed || event.pointerId !== dragState.id) return;
    const wasDragging = dragState.active;
    dragState.pressed = dragState.active = false;
    if (wasDragging) start(thrown(dragState.vx, dragState.vy), false);
  }
  let suppressClick = false;
  hitBox.addEventListener('pointerup', event => {
    // Ignore the click a drag produces, but don't eat a later tap if none arrives.
    if (dragState.active) {
      suppressClick = true;
      setTimeout(() => { suppressClick = false; }, 60);
    }
    release(event);
  });
  hitBox.addEventListener('pointercancel', release);
  // Also covers Enter and Space, so keyboard users get the same moves.
  hitBox.addEventListener('click', () => {
    if (suppressClick) { suppressClick = false; return; }
    reactToClick();
  });

  /* ---------- chat ---------- */

  const HISTORY_KEY = 'zenitsu-chat';
  const INTRO = "H-hi! Tell me what's on your mind, and I'll help you work out what you actually need and what it might take. Just please don't make me fight.";
  const SUGGESTIONS = ['I need a website', 'I want an app or a system', "I'm not sure what I need", 'What would my project cost?'];
  const FALLBACKS = {
    'slow-down': 'W-wait, too fast! Give me a minute to catch my breath.',
    busy: "I'm overwhelmed right now. Try again, or reach Isack directly.",
    resting: "I've talked all day and I'm falling asleep. Please reach Isack directly.",
    offline: "I can't answer right now, but Isack can.",
  };
  const chat = {
    open: false, thinking: false, messages: [],
    surface: { el: chatPanel, range: null, inset: 0 },
  };
  const chatLog = chatPanel.querySelector('.zenitsu-chat-log');
  const chatForm = chatPanel.querySelector('.zenitsu-chat-form');
  const chatInput = chatPanel.querySelector('input');
  const chatSend = chatForm.querySelector('button');
  const coarsePointer = () => matchMedia('(pointer: coarse)').matches;
  let suggestionsEl = null;

  const perch = () => (chat.open ? chat.surface : null);

  function leavePerch(surface) {
    if (pet.surface !== surface) return;
    pet.surface = null;
    pet.vx = 0; pet.vy = 0;
    if (rafId && !perch()) start(fly(), false);
  }

  // Follows the page: white with black buttons on Works, black with silver on Story.
  function syncTone() {
    const match = getComputedStyle(document.body).backgroundColor.match(/[\d.]+/g);
    if (!match || (match.length > 3 && Number(match[3]) === 0)) return;
    const [r, g, b] = match.map(Number);
    const tone = r * .299 + g * .587 + b * .114 < 128 ? 'dark' : 'light';
    [launcher, chatPanel].forEach(element => { if (element.dataset.tone !== tone) element.dataset.tone = tone; });
  }

  function addMessage(role, text, contact = false, retry = null) {
    const row = document.createElement('div');
    row.className = `zenitsu-msg zenitsu-msg-${role}`;
    const paragraph = document.createElement('p');
    paragraph.textContent = text;    // never as HTML: replies come from a model
    row.append(paragraph);
    if (contact || retry) {
      const actions = document.createElement('div');
      actions.className = 'zenitsu-msg-actions';
      if (retry) {
        const again = document.createElement('button');
        again.type = 'button';
        again.textContent = 'Try again';
        again.addEventListener('click', retry);
        actions.append(again);
      }
      if (contact) {
        const whatsapp = document.createElement('a');
        whatsapp.href = 'https://wa.me/255749498117';
        whatsapp.target = '_blank';
        whatsapp.rel = 'noopener';
        whatsapp.textContent = 'WhatsApp Isack';
        const email = document.createElement('a');
        email.href = 'mailto:lugata619@gmail.com';
        email.textContent = 'Email Isack';
        actions.append(whatsapp, email);
      }
      row.append(actions);
    }
    chatLog.append(row);
    chatLog.scrollTop = chatLog.scrollHeight;
    return row;
  }

  function renderIntro() {
    chatLog.textContent = '';
    const intro = document.createElement('div');
    intro.className = 'zenitsu-intro';
    const heading = document.createElement('h2');
    heading.textContent = "Hi, I'm Zenitsu.";
    const line = document.createElement('p');
    line.textContent = INTRO;
    intro.append(heading, line);
    chatLog.append(intro);
    suggestionsEl = null;
    if (chat.messages.length) return;
    suggestionsEl = document.createElement('div');
    suggestionsEl.className = 'zenitsu-suggestions';
    SUGGESTIONS.forEach(text => {
      const suggestion = document.createElement('button');
      suggestion.type = 'button';
      suggestion.innerHTML = '<span></span><svg viewBox="0 0 20 20" width="15" height="15" aria-hidden="true"><path d="M6 14L14 6M7.5 6H14v6.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      suggestion.firstElementChild.textContent = text;
      suggestion.addEventListener('click', () => sendMessage(text));
      suggestionsEl.append(suggestion);
    });
    chatLog.append(suggestionsEl);
  }

  function saveHistory() {
    try { sessionStorage.setItem(HISTORY_KEY, JSON.stringify(chat.messages)); } catch {}
  }

  function restoreChat() {
    try {
      const saved = JSON.parse(sessionStorage.getItem(HISTORY_KEY) || '[]');
      if (Array.isArray(saved)) chat.messages = saved.filter(m => m && typeof m.content === 'string' && (m.role === 'user' || m.role === 'assistant')).slice(-16);
    } catch {}
    renderIntro();
    chat.messages.forEach(message => addMessage(message.role, message.content));
  }

  function addTyping() {
    const row = document.createElement('div');
    row.className = 'zenitsu-msg zenitsu-msg-assistant zenitsu-typing';
    row.setAttribute('aria-label', 'Zenitsu is thinking');
    row.innerHTML = '<span></span><span></span><span></span>';
    chatLog.append(row);
    chatLog.scrollTop = chatLog.scrollHeight;
    return row;
  }

  async function sendMessage(text) {
    const content = text.trim().slice(0, 500);
    if (!content || chat.thinking) return;
    suggestionsEl?.remove();
    suggestionsEl = null;
    chat.messages.push({ role: 'user', content });
    const sentRow = addMessage('user', content);
    chatInput.value = '';
    chat.thinking = true;
    chatSend.disabled = true;
    const typing = addTyping();
    let reply = '', failure = '';
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 50000);
      const response = await fetch('/assistant/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // The server only needs role and text; keep requests within its history limit.
        body: JSON.stringify({ messages: chat.messages.slice(-16).map(({ role, content: value }) => ({ role, content: value.slice(0, role === 'user' ? 500 : 1500) })) }),
        signal: controller.signal,
      });
      clearTimeout(timeout);
      const data = await response.json().catch(() => ({}));
      if (response.ok && data.reply) {
        reply = data.reply;
      } else {
        failure = data.error || 'offline';
      }
    } catch {
      failure = 'busy';
    }
    typing.remove();
    chat.thinking = false;
    chatSend.disabled = false;
    if (failure) {
      // A failed turn stays out of the history; the visitor can retry without retyping.
      chat.messages.pop();
      sentRow.classList.add('zenitsu-msg-failed');
      const notice = addMessage('assistant', FALLBACKS[failure] || FALLBACKS.busy, failure !== 'slow-down', () => {
        sentRow.remove();
        notice.remove();
        sendMessage(content);
      });
    } else {
      chat.messages.push({ role: 'assistant', content: reply });
      chat.messages = chat.messages.slice(-16);
      addMessage('assistant', reply);
      saveHistory();
      // He's delighted with himself every time he gets an answer right.
      if (!motion.matches && !hidden && chat.open && rafId) start(slash());
    }
    if (chat.open && !coarsePointer()) chatInput.focus({ preventScroll: true });
    offerHandoff();
  }

  // Once there's something real to discuss, make reaching Isack one tap, with context.
  function offerHandoff() {
    chatLog.querySelector('.zenitsu-handoff')?.remove();
    const said = chat.messages.filter(message => message.role === 'user').map(message => message.content);
    if (said.length < 3 || chat.thinking) return;
    const text = `Hi Isack, I was chatting with Zenitsu on your site about a project:\n\n${said.map(line => `- ${line}`).join('\n')}`;
    const row = document.createElement('div');
    row.className = 'zenitsu-msg-actions zenitsu-handoff';
    const link = document.createElement('a');
    link.href = `https://wa.me/255749498117?text=${encodeURIComponent(text)}`;
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = 'Send this to Isack on WhatsApp';
    row.append(link);
    chatLog.append(row);
    chatLog.scrollTop = chatLog.scrollHeight;
  }

  function setOptions(open) {
    optionsPanel.hidden = !open;
    moreButton.setAttribute('aria-expanded', String(open));
  }

  function setChat(open) {
    if (open === chat.open) return;
    chat.open = open;
    chatPanel.hidden = !open;
    launcher.toggleAttribute('data-open', open);
    launcherButton.setAttribute('aria-expanded', String(open));
    launcherLabel.textContent = open ? 'Close' : 'Ask me';
    launcherButton.setAttribute('aria-label', open ? 'Close chat with Zenitsu' : "Ask Zenitsu, the site's AI guide");
    setOptions(false);
    if (open) {
      syncTone();
      fitToViewport();
      if (!chatLog.childElementCount) restoreChat();
      chatLog.scrollTop = chatLog.scrollHeight;
      if (rafId) start(hopOnto(chat.surface));
      // Opening a phone keyboard uninvited would hide the panel he just opened.
      if (!coarsePointer()) chatInput.focus({ preventScroll: true });
      else chatLog.focus({ preventScroll: true });
    } else {
      leavePerch(chat.surface);
    }
  }

  // Keep the composer above a phone's on-screen keyboard. The keyboard fires a burst of
  // viewport events while it slides; they are folded into one update per frame.
  let fitFrame = 0;
  function fitToViewport() {
    if (!fitFrame) fitFrame = requestAnimationFrame(fitNow);
  }
  function fitNow() {
    fitFrame = 0;
    const viewport = window.visualViewport;
    if (!viewport) return;
    const keyboard = Math.round(Math.max(0, innerHeight - viewport.height - viewport.offsetTop));
    const typing = keyboard > 80;
    // The newest message stays in view when the panel shrinks or grows around the keyboard.
    const atBottom = chatLog.scrollHeight - chatLog.scrollTop - chatLog.clientHeight < 40;
    chatPanel.style.setProperty('--zen-viewport', `${Math.round(viewport.height)}px`);
    chatPanel.style.setProperty('--zen-keyboard', `${keyboard}px`);
    if (typing !== keyboardOpen) {
      keyboardOpen = typing;
      chatPanel.toggleAttribute('data-keyboard', typing);
      launcher.toggleAttribute('data-keyboard', typing);
      layer.toggleAttribute('data-typing', typing);
    }
    if (atBottom) chatLog.scrollTop = chatLog.scrollHeight;
  }

  launcherButton.addEventListener('click', () => setChat(!chat.open));
  moreButton.addEventListener('click', () => setOptions(optionsPanel.hidden));
  chatPanel.querySelector('.zenitsu-chat-close').addEventListener('click', () => { setChat(false); launcherButton.focus({ preventScroll: true }); });
  chatForm.addEventListener('submit', event => { event.preventDefault(); sendMessage(chatInput.value); });
  // Tapping send must not take focus from the input, or the keyboard drops mid-send
  // and the panel jumps while the message is going out.
  chatSend.addEventListener('pointerdown', event => { if (document.activeElement === chatInput) event.preventDefault(); });
  // While typing, a drag on the page behind would pan the phone's viewport and drag the
  // panel with it. Only the conversation itself scrolls then.
  document.addEventListener('touchmove', event => {
    if (keyboardOpen && chat.open && !chatLog.contains(event.target)) event.preventDefault();
  }, { passive: false });
  window.visualViewport?.addEventListener('resize', fitToViewport);
  window.visualViewport?.addEventListener('scroll', fitToViewport);

  /* ---------- lifecycle ---------- */

  function stop() {
    cancelAnimationFrame(rafId);
    rafId = 0;
    behavior = null;
  }

  function apply() {
    stop();
    layer.hidden = hidden;
    visibility.textContent = hidden ? 'Bring Zenitsu back on the page' : 'Hide Zenitsu from the page';
    if (hidden) return;
    measure();
    pet.surface = null;
    pet.airborne = false;
    pet.pivotBody = false;
    pet.rot = 0;
    if (motion.matches) {
      // Reduced motion: a still figure in the corner, nothing moving or clickable.
      pet.x = viewW() - 150;
      pet.y = floorY();
      pet.dir = -1;
      layer.dataset.still = '';
      show('idle', 0);
      draw();
      return;
    }
    delete layer.dataset.still;
    let opening = entrance;
    if (perch()) opening = () => hopOnto(perch());
    start(opening(), false);
    lastTime = performance.now();
    rafId = requestAnimationFrame(tick);
  }

  visibility.addEventListener('click', () => {
    hidden = !hidden;
    try { localStorage.setItem(STORAGE_KEY, hidden ? '1' : '0'); } catch {}
    setOptions(false);
    apply();
  });
  document.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    if (!optionsPanel.hidden) { setOptions(false); moreButton.focus({ preventScroll: true }); }
    else if (chat.open) { setChat(false); launcherButton.focus({ preventScroll: true }); }
  });
  document.addEventListener('pointerdown', event => {
    if (!optionsPanel.hidden && !optionsPanel.contains(event.target) && !moreButton.contains(event.target)) setOptions(false);
  });
  motion.addEventListener('change', apply);
  // He goes into the castle gallery in person, and blinks back in when it closes.
  addEventListener('castle:enter', () => { setChat(false); stop(); });
  addEventListener('castle:leave', apply);
  addEventListener('resize', () => {
    if (hidden) return;
    measure();
    pet.x = clamp(pet.x, 16, viewW() - 16);
    if (!pet.surface && !pet.airborne) pet.y = floorY();
    draw();
  });

  document.body.append(layer, chatPanel, launcher);
  syncTone();
  // The site's client router changes the page colour without a reload. Check when the
  // route changes (and once the page transition has painted) instead of polling.
  const toneAfterRoute = () => { syncTone(); setTimeout(syncTone, 350); setTimeout(syncTone, 1200); };
  for (const method of ['pushState', 'replaceState']) {
    const original = history[method];
    history[method] = function (...args) {
      const result = original.apply(this, args);
      toneAfterRoute();
      return result;
    };
  }
  addEventListener('popstate', toneAfterRoute);
  // Preload every strip so moves never flash blank, but only once the page itself has
  // finished loading, so 600 KB of sprites never compete with the page's own images.
  const preload = () => Object.values(SHEETS).forEach(({ src }) => { new Image().src = src; });
  const preloadWhenIdle = () => ('requestIdleCallback' in window ? requestIdleCallback(preload, { timeout: 2500 }) : setTimeout(preload, 800));
  if (document.readyState === 'complete') preloadWhenIdle();
  else addEventListener('load', preloadWhenIdle, { once: true });
  setTimeout(apply, 900);
})();
