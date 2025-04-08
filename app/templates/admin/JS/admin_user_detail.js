document.addEventListener("DOMContentLoaded", () => {
    const warningForms = document.querySelectorAll("form.inline-form");
  
    warningForms.forEach(form => {
      form.addEventListener("submit", function (e) {
        const button = form.querySelector("button");
        const message = button.classList.contains("btn-warning")
          ? "Opravdu chcete skrýt tuto objednávku klientovi?"
          : "Opravdu chcete obnovit tuto objednávku pro klienta?";
        if (!confirm(message)) {
          e.preventDefault();
        }
      });
    });
  });
  