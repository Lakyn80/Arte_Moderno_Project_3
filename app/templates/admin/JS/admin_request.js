// Inicializace DataTables pro tabulku požadavků
$(document).ready(function () {
    $(".admin-table").DataTable({
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf", "print"],
      language: {
        url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/cs.json",
      },
      order: [[0, "desc"]], // Seřadit podle ID sestupně
    });
  });
  