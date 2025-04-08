document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const emailInput = document.querySelector("input[name='email']");

  form.addEventListener("submit", function (event) {
    const email = emailInput.value.trim();
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!email) {
      alert("⚠️ Prosím, vyplňte e-mailovou adresu.");
      event.preventDefault();
      return;
    }

    if (!emailRegex.test(email)) {
      alert("⚠️ Zadejte platnou e-mailovou adresu.");
      event.preventDefault();
    }
  });
});
