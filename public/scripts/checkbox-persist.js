/**
 * Grocery checkbox persistence — kitchen.kaleb.one
 * Uses sessionStorage to persist checkbox state per page.
 * Uses label text as key (no data-id attributes needed).
 */
(function() {
  function getCheckboxKey(cb, index) {
    var li = cb.closest('li');
    var label = li ? li.querySelector('label') : null;
    var text = label ? label.textContent.trim() : '';
    return 'g_' + window.location.pathname + '_' + (text || 'cb' + index);
  }

  document.addEventListener('DOMContentLoaded', function() {
    var checkboxes = document.querySelectorAll('.grocery-list input[type="checkbox"]');
    checkboxes.forEach(function(cb, index) {
      var key = getCheckboxKey(cb, index);
      if (sessionStorage.getItem(key) === '1') {
        cb.checked = true;
        if (cb.closest('li')) cb.closest('li').classList.add('checked');
      }
      cb.addEventListener('change', function() {
        if (cb.closest('li')) cb.closest('li').classList.toggle('checked', cb.checked);
        cb.checked ? sessionStorage.setItem(key, '1') : sessionStorage.removeItem(key);
      });
    });

    var btn = document.querySelector('.reset-btn');
    if (btn) {
      btn.addEventListener('click', function() {
        checkboxes.forEach(function(cb, index) {
          cb.checked = false;
          if (cb.closest('li')) cb.closest('li').classList.remove('checked');
          sessionStorage.removeItem(getCheckboxKey(cb, index));
        });
      });
    }
  });
})();