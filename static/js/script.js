// Initialize DataTable
$(document).ready(function () {
    $('#caseTable').DataTable();
});

// Initialize Leaflet Map
const map = L.map('map').setView([44.5, -93.0], 6); // Center of Minnesota
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
}).addTo(map);

// Add Markers for Job and Housing Locations
fetch("/case.json")
    .then(response => response.json())
    .then(data => {
        data.forEach(item => {
            // Job Location Marker
            const jobPopup = `<b>Job:</b> ${item.empBusinessName}<br>${item.clearanceOrder.jobCity}, ${item.clearanceOrder.jobState}`;
            L.marker([44.5, -93.0]) // Update coordinates based on job location
                .addTo(map)
                .bindPopup(jobPopup);

            // Housing Location Marker
            const housingPopup = `<b>Housing:</b> ${item.housingAddr1}<br>${item.housingCity}, ${item.housingState}`;
            L.marker([44.1, -93.0]) // Update coordinates based on housing location
                .addTo(map)
                .bindPopup(housingPopup);
        });
    });