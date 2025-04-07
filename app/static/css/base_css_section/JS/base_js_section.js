// Automatické skrytí flash zpráv
setTimeout(function () {
  const flashMessages = document.querySelectorAll(".flash-message");
  flashMessages.forEach((msg) => {
    msg.style.opacity = "0";
    setTimeout(() => msg.remove(), 500);
  });
}, 5000);

// CSRF token
window.CSRF_TOKEN = document
  .querySelector('meta[name="csrf-token"]')
  .getAttribute("content");

// Jazykový burger – otevření a zavření
document.addEventListener("DOMContentLoaded", () => {
  const burger = document.querySelector(".lang-burger");
  const menu = burger?.querySelector(".lang-menu");

  if (burger && menu) {
    burger.addEventListener("click", (e) => {
      e.stopPropagation();
      menu.classList.toggle("show");
    });

    document.addEventListener("click", (e) => {
      if (!burger.contains(e.target)) {
        menu.classList.remove("show");
      }
    });
  }
});
