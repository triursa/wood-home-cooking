// Shared layout injection
(function() {
  // ── CONFIGURE THIS ────────────────────────────────────────────────────────
  // The base path for the site. Must match your GitHub Pages URL.
  // e.g. if your site is https://triursa.github.io/wood-home-cooking/
  // then BASE = '/wood-home-cooking'
  const BASE = '/wood-home-cooking';
  // ─────────────────────────────────────────────────────────────────────────

  const root = BASE + '/';
  const path = window.location.pathname;

  function r(p) { return root + p; }

  function isActive(section) {
    return path.includes('/' + section + '/') ? 'class="active"' : '';
  }

  const header = `
<header class="site-header">
  <div class="site-wrapper">
    <a href="${root}" class="site-title">Wood Home Cooking <span>/ Kaleb &amp; Minny</span></a>
    <nav>
      <a href="${r('recipes/')}" ${isActive('recipes')}>Recipes</a>
      <a href="${r('meal-plans/')}" ${isActive('meal-plans')}>Meal Plans</a>
      <a href="${r('grocery-lists/')}" ${isActive('grocery-lists')}>Grocery Lists</a>
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
