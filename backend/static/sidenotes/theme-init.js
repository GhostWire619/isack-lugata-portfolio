// Apply before styles paint so navigation never flashes the opposite theme.
(() => {
  const root = document.documentElement;
  const system = matchMedia('(prefers-color-scheme: dark)');
  let saved;
  try { saved = localStorage.getItem('journal-theme'); } catch {}
  const apply = theme => {
    root.dataset.theme = theme;
    root.classList.remove('w-theme-system', 'w-theme-light', 'w-theme-dark');
    root.classList.add('w-theme-' + theme);
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.setAttribute('aria-pressed', String(theme === 'dark'));
      button.setAttribute('aria-label', 'Switch to ' + (theme === 'dark' ? 'light' : 'dark') + ' mode');
      button.title = button.getAttribute('aria-label');
    });
  };
  apply(saved === 'light' || saved === 'dark' ? saved : system.matches ? 'dark' : 'light');
  document.addEventListener('DOMContentLoaded', () => {
    apply(root.dataset.theme);
    document.querySelectorAll('[data-theme-toggle]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => {
        saved = root.dataset.theme === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem('journal-theme', saved); } catch {}
        apply(saved);
      });
    });
  });
  system.addEventListener('change', event => { if (!saved) apply(event.matches ? 'dark' : 'light'); });
  addEventListener('storage', event => {
    if (event.key === 'journal-theme') {
      saved = event.newValue;
      apply(saved === 'light' || saved === 'dark' ? saved : system.matches ? 'dark' : 'light');
    }
  });
})();
