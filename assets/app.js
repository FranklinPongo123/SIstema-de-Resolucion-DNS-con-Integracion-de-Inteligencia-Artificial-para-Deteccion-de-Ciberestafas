document.addEventListener('click', function (event) {
  const button = event.target.closest('[data-domain]');
  if (!button) return;
  const input = document.getElementById('domain');
  if (input) { input.value = button.dataset.domain; input.focus(); }
});
