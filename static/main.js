// main.js
// This file is intentionally minimal to support front-end interactions.

// Close the modal when clicking outside its content.
document.addEventListener('click', function (event) {
  const modal = document.getElementById('manualPunchModal') || document.getElementById('addEmployeeModal') || document.getElementById('addShiftModal');
  if (!modal) return;

  if (!modal.classList.contains('hidden') && event.target === modal) {
    modal.classList.add('hidden');
  }
});

// Prevent extra form submission warnings if the browser auto-fills hidden fields.
window.addEventListener('load', function () {
  const forms = document.querySelectorAll('form');
  forms.forEach(function (form) {
    form.addEventListener('submit', function () {
      const submitButton = form.querySelector('button[type="submit"]');
      if (submitButton) submitButton.disabled = true;
    });
  });
});
