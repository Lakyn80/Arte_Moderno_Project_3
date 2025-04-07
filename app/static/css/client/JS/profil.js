document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.querySelector("#datepicker");
  
    if (dateInput) {
      flatpickr(dateInput, {
        dateFormat: "Y-m-d",
        maxDate: "today",
        altInput: true,
        altFormat: "d.m.Y",
        allowInput: true,
      });
    }
  });
  