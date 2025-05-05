
window.onload = function () {
    if ("geolocation" in navigator) {
        navigator.geolocation.getCurrentPosition(function (position) {
            fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${position.coords.latitude}&longitude=${position.coords.longitude}&localityLanguage=en`)
                .then(res => res.json())
                .then(data => {
                    document.querySelector('#id_city').value = data.city || '';
                    document.querySelector('#id_state').value = data.principalSubdivision || '';
                });
        });
    }
};

