document.addEventListener("DOMContentLoaded", () => {
  // === CSRF token z hidden input nebo <meta> ===
  const csrfToken =
    document.querySelector('[name="csrf_token"]')?.value ||
    document.querySelector('meta[name="csrf-token"]')?.getAttribute("content");

  // === Aktualizace počtu položek v navbaru ===
  function updateCartCount() {
    fetch("/cart/count", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        const cartCountElement = document.getElementById("cart-count");
        if (cartCountElement) {
          cartCountElement.innerText = data.cart_item_count;
        }
      })
      .catch((error) =>
        console.error("Chyba při aktualizaci počtu položek:", error)
      );
  }

  // === Přidání produktu do košíku ===
  document.querySelectorAll(".buy-button").forEach((button) => {
    button.addEventListener("click", function () {
      const productId = this.dataset.productId;

      fetch("/cart/add", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken && { "X-CSRFToken": csrfToken }),
        },
        body: JSON.stringify({ product_id: productId }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.error) {
            alert(data.error);
          } else {
            alert(data.message);
            updateCartCount();
          }
        })
        .catch((error) => {
          console.error("Chyba:", error);
          alert("Došlo k chybě při přidávání do košíku.");
        });
    });
  });

  // === Odebrání produktu z košíku ===
  document.querySelectorAll(".remove-from-cart").forEach((button) => {
    button.addEventListener("click", function () {
      const productId = this.dataset.productId;

      fetch("/cart/remove", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken && { "X-CSRFToken": csrfToken }),
        },
        body: JSON.stringify({ product_id: productId }),
      })
        .then((response) => response.json())
        .then((data) => {
          alert(data.message);
          updateCartCount();

          const productRow = document.querySelector(
            `tr[data-product-id="${productId}"]`
          );
          if (productRow) {
            productRow.remove();
          }

          // Pokud není v košíku nic, ukaž hlášku
          const remainingItems = document.querySelectorAll(".cart-item-row");
          if (remainingItems.length === 0) {
            const container = document.querySelector(".cart-container");
            if (container) {
              container.innerHTML = "<p>Váš košík je prázdný.</p>";
            }
          }
        })
        .catch((error) => {
          console.error("Chyba:", error);
          alert("Došlo k chybě při odebírání z košíku.");
        });
    });
  });

  // === Odebrání po jedné nebo všech – z řádku v tabulce ===
  document.querySelectorAll(".cart-item-row").forEach((row) => {
    const productId = row.dataset.productId;

    const handleRemove = async (url, button) => {
      button.disabled = true;
      const originalText = button.innerHTML;
      button.innerHTML = "⏳";

      await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(csrfToken && { "X-CSRFToken": csrfToken }),
        },
        body: JSON.stringify({ product_id: productId }),
      });

      location.reload();
    };

    row.querySelector(".remove-one")?.addEventListener("click", (e) => {
      handleRemove("/cart/remove_one", e.target);
    });

    row.querySelector(".remove-all")?.addEventListener("click", (e) => {
      handleRemove("/cart/remove_all", e.target);
    });
  });

  // === Načti počet položek při otevření stránky ===
  updateCartCount();
});
