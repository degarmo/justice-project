document.addEventListener('DOMContentLoaded', function () {
    var map = L.map('map').setView([20, 0], 2);

// Add search bar (geocoder)
L.Control.geocoder({
    defaultMarkGeocode: false
})
.on('markgeocode', function(e) {
    var bbox = e.geocode.bbox;
    var poly = L.polygon([
        bbox.getSouthEast(),
        bbox.getNorthEast(),
        bbox.getNorthWest(),
        bbox.getSouthWest()
    ]).addTo(map);
    map.fitBounds(poly.getBounds());
})
.addTo(map);


    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    var markerCluster = L.markerClusterGroup();
    var allMarkers = [];  // Store markers and data for reset

    var heatLayer = null;
    var heatEnabled = false;

    // Fetch visitor logs once and populate both clusters and heatmap
    fetch('/api/visitor-logs/')
        .then(response => response.json())
        .then(data => {
            data.forEach(log => {
                if (log.latitude && log.longitude) {
                    var marker = L.marker([log.latitude, log.longitude])
                        .bindPopup(
                            `<b>IP:</b> ${log.ip_address}<br>
                             <b>ISP:</b> ${log.isp}<br>
                             <b>Device:</b> ${log.device}<br>
                             <b>VPN:</b> ${log.vpn_status ? 'Yes' : 'No'}<br>
                             <b>Tor:</b> ${log.tor_status ? 'Yes' : 'No'}<br>
                             <b>City:</b> ${log.city}, ${log.region}, ${log.country}<br>
                             <b>Timestamp:</b> ${log.timestamp}`
                        );
                    markerCluster.addLayer(marker);
                    allMarkers.push([log.latitude, log.longitude, 0.5]);  // For heatmap
                }
            });

            map.addLayer(markerCluster);  // Show clusters by default
        });

    // Toggle heatmap
    document.getElementById('toggleHeatmap').addEventListener('click', function () {
        heatEnabled = !heatEnabled;

        if (heatEnabled) {
            heatLayer = L.heatLayer(allMarkers, {
                radius: 25,
                blur: 15,
                maxZoom: 10,
            }).addTo(map);
            map.removeLayer(markerCluster);  // Hide clusters
        } else {
            map.removeLayer(heatLayer);
            map.addLayer(markerCluster);  // Show clusters again
        }
    });
});



