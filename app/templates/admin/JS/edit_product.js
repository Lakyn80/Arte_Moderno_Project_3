document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("image");
  const previewContainer = document.getElementById("preview-container");

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      const file = this.files[0];

      // Vyprázdnit předchozí náhled
      if (previewContainer) {
        previewContainer.innerHTML = "";
      }

      if (!file) return;

      const allowedTypes = ["image/jpeg", "image/png", "image/webp"];
      const maxSizeMB = 5;

      if (!allowedTypes.includes(file.type)) {
        alert("Povoleny jsou pouze obrázky JPG, PNG nebo WEBP.");
        this.value = "";
        return;
      }

      if (file.size > maxSizeMB * 1024 * 1024) {
        alert("Maximální velikost souboru je 5 MB.");
        this.value = "";
        return;
      }

      // ✅ Náhled obrázku
      const reader = new FileReader();
      reader.onload = function (e) {
        const img = document.createElement("img");
        img.src = e.target.result;
        img.alt = "Náhled obrázku";
        img.style.maxWidth = "200px";
        img.style.marginTop = "10px";
        if (previewContainer) {
          previewContainer.appendChild(img);
        }
      };
      reader.readAsDataURL(file);
    });
  }
});
