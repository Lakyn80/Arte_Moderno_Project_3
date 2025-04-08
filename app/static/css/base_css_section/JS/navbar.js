document.addEventListener("DOMContentLoaded", function () {
  const langBurger = document.querySelector(".lang-burger");
  const langMenu = langBurger?.querySelector(".lang-menu");

  if (langBurger && langMenu) {
    // Kliknutí na 🌐
    langBurger.addEventListener("click", function (e) {
      e.stopPropagation(); // Zastaví šíření události
      langMenu.classList.toggle("show"); // Přepne třídu
    });

    // Klik mimo zavře menu
    document.addEventListener("click", function (e) {
      if (!langBurger.contains(e.target)) {
        langMenu.classList.remove("show");
      }
    });

    // Zavření po kliknutí na jazyk
    langMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        langMenu.classList.remove("show");
      });
    });
  }
});
