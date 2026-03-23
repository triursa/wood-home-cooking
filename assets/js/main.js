// Shared layout injection
(function() {
  const path = window.location.pathname;

  // Dynamically determine the repo root.
  // GitHub Pages project sites live at /<repo-name>/...
  // We detect depth by counting path segments and back up to root accordingly.
  // Works for: /wood-home-cooking/, /wood-home-cooking/recipes/, etc.
  // Also works when running locally from file:// (root = '/')

  function getRoot() {
    // file:// local preview
    if (window.location.protocol === 'file:') return './';

    const segments = path.split('/').filter(Boolean);
    // GitHub Pages: first segment is the repo name
    // pages at root: /repo/            -> depth 0, root = /repo/
    // pages at depth 1: /repo/recipes/ -> root = /repo/
    // pages at depth 2: /repo/a/b.html -> root = /repo/
    if (segments.length === 0) return '/';
    const repoName = segments[0];
    return '/' + repoName + '/';
  }

  const root = getRoot();

  function r(p) { return root + p; }

  // Active nav detection
  function isActive(section) {
    return path.includes('/' + section + '/') ? 'class="active"' : '';
  }

  // Inject header
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

  // Grocery checkbox persistence (session only — resets when tab closes)
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.grocery-list input[type="checkbox"]').forEach(cb => {
      const key = 'g_' + path + '_' + cb.dataset.id;
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
        sessionStorage.removeItem('g_' + path + '_' + cb.dataset.id);
      });
    });
  });
})();
