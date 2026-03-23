// Shared layout injection
(function() {
  // Determine depth for relative paths
  const path = window.location.pathname;
  const depth = (path.match(/\//g) || []).length - 1;
  // For GitHub Pages project site: /wood-meal-plan/... has depth >= 1
  // We need to find the root
  const segments = path.split('/').filter(Boolean);
  // root is always /wood-meal-plan/
  let root = '/wood-meal-plan/';
  // if running locally from file or different base, fall back
  if (!path.includes('wood-meal-plan')) root = '/';

  function r(p) { return root + p; }

  // Inject CSS link if not present
  if (!document.querySelector('link[data-shared]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.setAttribute('data-shared', '1');
    link.href = root + 'assets/css/style.css';
    document.head.appendChild(link);
  }

  // Header
  const currentPath = window.location.pathname;
  function isActive(section) {
    return currentPath.includes('/' + section + '/') ? 'class="active"' : '';
  }

  const header = `
<header class="site-header">
  <div class="site-wrapper">
    <a href="${root}" class="site-title">Wood Home Cooking <span>/ Kaleb &amp; Minny</span></a>
    <nav>
      <a href="${r('recipes/')}" ${isActive('recipes')}>Recipes</a>
      <a href="${r('meal-plans/')}" ${isActive('meal-plans')}>Meal Plans</a>
      <a href="${r('knowledge-base/preferences.html')}" ${isActive('knowledge-base')}>Guidelines</a>
    </nav>
  </div>
</header>`;

  const footer = `
<footer>
  <div class="site-wrapper">
    Wood Home Cooking &mdash; Kaleb &amp; Minny &mdash; Kyle, TX
  </div>
</footer>`;

  document.body.insertAdjacentHTML('afterbegin', header);
  document.body.insertAdjacentHTML('beforeend', footer);

  // Grocery checkbox persistence
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.grocery-list input[type="checkbox"]').forEach(cb => {
      const key = 'g_' + window.location.pathname + '_' + cb.dataset.id;
      if (sessionStorage.getItem(key) === '1') {
        cb.checked = true;
        cb.closest('li').classList.add('checked');
      }
      cb.addEventListener('change', () => {
        cb.closest('li').classList.toggle('checked', cb.checked);
        cb.checked ? sessionStorage.setItem(key, '1') : sessionStorage.removeItem(key);
      });
    });
    const btn = document.querySelector('.reset-btn');
    if (btn) btn.addEventListener('click', () => {
      document.querySelectorAll('.grocery-list input[type="checkbox"]').forEach(cb => {
        cb.checked = false;
        cb.closest('li').classList.remove('checked');
        sessionStorage.removeItem('g_' + window.location.pathname + '_' + cb.dataset.id);
      });
    });
  });
})();
