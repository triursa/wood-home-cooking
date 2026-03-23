// Grocery list checkbox persistence
document.addEventListener('DOMContentLoaded', () => {
  const checkboxes = document.querySelectorAll('.grocery-list input[type="checkbox"]');

  // Restore saved state
  checkboxes.forEach(cb => {
    const key = 'grocery_' + window.location.pathname + '_' + cb.dataset.id;
    if (sessionStorage.getItem(key) === 'checked') {
      cb.checked = true;
      cb.closest('li').classList.add('checked');
    }
    cb.addEventListener('change', () => {
      cb.closest('li').classList.toggle('checked', cb.checked);
      if (cb.checked) {
        sessionStorage.setItem(key, 'checked');
      } else {
        sessionStorage.removeItem(key);
      }
    });
  });

  // Reset button
  const resetBtn = document.getElementById('grocery-reset');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      checkboxes.forEach(cb => {
        cb.checked = false;
        cb.closest('li').classList.remove('checked');
        const key = 'grocery_' + window.location.pathname + '_' + cb.dataset.id;
        sessionStorage.removeItem(key);
      });
    });
  }
});
