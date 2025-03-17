// Add functionality to the Export buttons
document.getElementById('export-csv').addEventListener('click', function () {
    const reportType = document.getElementById('report-type').value;
    window.location.href = `{% url 'VMS:reports' %}?export_csv=1&report_type=${reportType}`;
});

document.getElementById('export-pdf').addEventListener('click', function () {
    const reportType = document.getElementById('report-type').value;
    window.location.href = `{% url 'VMS:reports' %}?export_pdf=1&report_type=${reportType}`;
});