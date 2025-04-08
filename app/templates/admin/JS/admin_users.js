// admin_users.js – DataTables inicializace pro seznam uživatelů

document.addEventListener("DOMContentLoaded", function () {
  const table = document.querySelector(".admin-table");
  if (table) {
    $(table).DataTable({
      language: {
        url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/cs.json",
      },
      pageLength: 25,
    });
  }
});
