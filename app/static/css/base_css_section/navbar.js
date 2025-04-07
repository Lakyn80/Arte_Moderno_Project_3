document.addEventListener("DOMContentLoaded", function () {
  const langBurger = document.querySelector(".lang-burger");
  const langMenu = document.querySelector(".lang-menu");

  if (langBurger && langMenu) {
    langBurger.addEventListener("click", function (e) {
      e.stopPropagation();
      langMenu.classList.toggle("show");
    });

    // Zavření menu při kliknutí mimo
    document.addEventListener("click", function (e) {
      if (!langBurger.contains(e.target)) {
        langMenu.classList.remove("show");
      }
    });

    // Zavření při výběru jazyka
    langMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        langMenu.classList.remove("show");
      });
    });
  }
});
