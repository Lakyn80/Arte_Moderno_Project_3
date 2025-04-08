// JavaScript pro inicializaci DataTables s exportními funkcemi
$(document).ready(function () {
  $("#orders-table").DataTable({
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "pdf", "print"],
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/cs.json",
    },
  });
});
