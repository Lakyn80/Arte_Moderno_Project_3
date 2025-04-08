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
  ?.getAttribute("content");

// Jazykový burger – otevření a zavření
document.addEventListener("DOMContentLoaded", function () {
  console.log("🍔 Jazykový burger aktivní!"); // 🧪 TEST

  const burger = document.querySelector(".lang-burger");
  const menu = document.querySelector(".lang-menu");

  if (!burger || !menu) {
    console.log("❌ Burger nebo menu nenalezeno");
    return;
  }

  burger.addEventListener("click", function (e) {
    e.stopPropagation();
    menu.classList.toggle("show");
    console.log("✅ Kliknuto na burger – toggle show");
  });

  document.addEventListener("click", function (e) {
    if (!burger.contains(e.target)) {
      menu.classList.remove("show");
    }
  });

  menu.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      menu.classList.remove("show");
    });
  });
});
