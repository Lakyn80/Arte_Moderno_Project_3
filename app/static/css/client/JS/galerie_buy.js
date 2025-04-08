document.addEventListener("DOMContentLoaded", () => {
  const buttons = document.querySelectorAll(".buy-button");

  // Získání CSRF tokenu z <meta>
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");

  buttons.forEach((button) => {
    button.addEventListener("click", async () => {
      const productId = button.getAttribute("data-product-id");

      const response = await fetch("/cart/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken, // ← DŮLEŽITÉ!
        },
        body: JSON.stringify({ product_id: productId }),
      });

      try {
        const data = await response.json();

        if (response.ok) {
          alert(data.message);

          // Aktualizace počtu produktů v košíku
          const countRes = await fetch("/cart/count");
          const countData = await countRes.json();
          const cartCount = document.getElementById("cart-count");
          if (cartCount) {
            cartCount.textContent = countData.cart_item_count;
          }
        } else {
          alert(data.message || "Nastala chyba.");
        }
      } catch (err) {
        alert("Chyba: server nevrátil platný JSON.");
        console.error("Chybná odpověď:", err);
      }
    });
  });
});
