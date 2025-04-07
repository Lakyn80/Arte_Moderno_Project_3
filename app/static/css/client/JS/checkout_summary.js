document.addEventListener("DOMContentLoaded", function () {
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
  document.getElementById("timezone").value = tz;
});

