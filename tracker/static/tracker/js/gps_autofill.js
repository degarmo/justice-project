
document.getElementById('share-location').addEventListener('change', function() {
    if (this.checked) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                document.getElementById('latitude').value = position.coords.latitude;
                document.getElementById('longitude').value = position.coords.longitude;
            }, function(error) {
                alert("Location permission denied or unavailable.");
                // Optional: uncheck the box or notify user
                document.getElementById('share-location').checked = false;
            });
        } else {
            alert("Geolocation is not supported by your browser.");
        }
    } else {
        // Reset location fields if unchecked
        document.getElementById('latitude').value = '';
        document.getElementById('longitude').value = '';
    }
});

