$(document).ready(function () {
  $("#orders-table tfoot th").each(function () {
    var title = $(this).text();
    $(this).html('<select><option value="">Vše</option></select>');
  });

  var table = $("#orders-table").DataTable({
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "pdf", "print"],
    language: {
      url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/cs.json",
    },
    initComplete: function () {
      this.api()
        .columns()
        .every(function () {
          var column = this;
          var select = $("select", column.footer());

          column
            .data()
            .unique()
            .sort()
            .each(function (d) {
              var cleanText = $("<div>").html(d).text();
              if (!select.find("option[value='" + cleanText + "']").length) {
                select.append(
                  '<option value="' + cleanText + '">' + cleanText + "</option>"
                );
              }
            });

          select.on("change", function () {
            var val = $.fn.dataTable.util.escapeRegex($(this).val());
            column.search(val ? "^" + val + "$" : "", true, false).draw();
          });
        });
    },
  });
});
