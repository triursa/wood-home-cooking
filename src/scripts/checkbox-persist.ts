/**
 * Grocery checkbox persistence — kitchen.kaleb.one
 *
 * Persists checkbox state in sessionStorage so checked items
 * survive page navigation but reset when the tab closes.
 * Migrated from original main.js — the ONLY interactive JS on kitchen.
 */
(function() {
  var path = window.location.pathname;

  document.addEventListener('DOMContentLoaded', function() {
    // Restore + bind grocery checkboxes
    document.querySelectorAll('.grocery-list input[type="checkbox"]').forEach(function(cb) {
      var key = 'g_' + path + '_' + cb.dataset.id;
      if (sessionStorage.getItem(key) === '1') {
        cb.checked = true;
        cb.closest('li').classList.add('checked');
      }
      cb.addEventListener('change', function() {
        cb.closest('li').classList.toggle('checked', cb.checked);
        cb.checked ? sessionStorage.setItem(key, '1') : sessionStorage.removeItem(key);
      });
    });

    // Reset button
    var btn = document.querySelector('.reset-btn');
    if (btn) {
      btn.addEventListener('click', function() {
        document.querySelectorAll('.grocery-list input[type="checkbox"]').forEach(function(cb) {
          cb.checked = false;
          cb.closest('li').classList.remove('checked');
          sessionStorage.removeItem('g_' + path + '_' + cb.dataset.id);
        });
      });
    }
  });
})();