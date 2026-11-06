(() => {
  function update() {
    document.querySelectorAll('.portfolio-extra-nav a').forEach(link => {
      if (new URL(link.href).pathname === location.pathname) link.setAttribute('aria-current','page');
      else link.removeAttribute('aria-current');
    });
  }
  addEventListener('popstate',update);
  document.addEventListener('portfolio:route',update);
  update();
})();
