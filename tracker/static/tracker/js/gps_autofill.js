
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
function fillCityStateFromCoords(lat, lon) {
    fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('id_city').value = data.city || '';
            document.getElementById('id_state').value = data.principalSubdivision || '';
            document.getElementById('id_latitude').value = position.coords.latitude;
            document.getElementById('id_longitude').value = position.coords.longitude;
        })
        .catch(err => console.warn("Failed to fetch geolocation data:", err));
}

    document.addEventListener("DOMContentLoaded", function () {
        const btn = document.getElementById("getLocationBtn");
        btn.addEventListener("click", function () {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function (position) {
                        const lat = position.coords.latitude;
                        const lon = position.coords.longitude;
                        console.log("Got location:", lat, lon);  // ✅ Debug
    
                        document.getElementById('id_latitude').value = position.coords.latitude;
                        document.getElementById('id_longitude').value = position.coords.longitude;
                    },
                    function (error) {
                        alert("Error getting location: " + error.message);
                    }
                );
            } else {
                alert("Geolocation is not supported by this browser.");
            }
        });
    });
 
function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        zoom: 4,
        center: { lat: 39.5, lng: -98.35 }  // USA center
    });
    locations.forEach(loc => {
        if (loc.latitude && loc.longitude) {
            new google.maps.Marker({
                position: { lat: loc.latitude, lng: loc.longitude },
                map: map,
                title: loc.display_name || "Anonymous"
            });
        }
    });
}
