/**
 * Grocery checkbox persistence — kitchen.kaleb.one
 *
 * Persists checkbox state in sessionStorage so checked items
 * survive page navigation but reset when the tab closes.
 * Migrated from original main.js — the ONLY interactive JS on kitchen.
 *
 * Uses label text as the storage key (since data-id is not generated
 * by the Astro markdown pipeline).
 */
(function() {
  function getCheckboxKey(cb, index) {
    var label = cb.closest('li')?.querySelector('label');
    var text = label ? label.textContent.trim() : '';
    return 'g_' + window.location.pathname + '_' + (text || 'cb' + index);
  }

  document.addEventListener('DOMContentLoaded', function() {
    // Restore + bind grocery checkboxes
    var checkboxes = document.querySelectorAll('.grocery-list input[type="checkbox"]');
    checkboxes.forEach(function(cb, index) {
      var key = getCheckboxKey(cb, index);
      if (sessionStorage.getItem(key) === '1') {
        cb.checked = true;
        cb.closest('li')?.classList.add('checked');
      }
      cb.addEventListener('change', function() {
        cb.closest('li')?.classList.toggle('checked', cb.checked);
        cb.checked ? sessionStorage.setItem(key, '1') : sessionStorage.removeItem(key);
      });
    });

    // Reset button
    var btn = document.querySelector('.reset-btn');
    if (btn) {
      btn.addEventListener('click', function() {
        checkboxes.forEach(function(cb, index) {
          cb.checked = false;
          cb.closest('li')?.classList.remove('checked');
          sessionStorage.removeItem(getCheckboxKey(cb, index));
        });
      });
    }
  });
})();