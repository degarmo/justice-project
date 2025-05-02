document.addEventListener('DOMContentLoaded', function () {
    var map = L.map('map').setView([39.5, -98.35], 4); // Center of US

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(map);

    fetch('/api/visitor-logs/')
        .then(response => response.json())
        .then(data => {
            data.forEach(log => {
                if (log.latitude && log.longitude) {
                    L.marker([log.latitude, log.longitude])
                        .addTo(map)
                        .bindPopup(`
                            <b>IP:</b> ${log.ip_address}<br>
                            <b>City:</b> ${log.city}<br>
                            <b>VPN:</b> ${log.vpn_status ? 'Yes' : 'No'}
                        `);
                }
            });
        });
});
