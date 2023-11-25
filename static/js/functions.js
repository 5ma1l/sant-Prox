function validateInputs() {
    var latitudeInput = document.getElementsByName('latitude')[0];
    var longitudeInput = document.getElementsByName('longitude')[0];

    if (latitudeInput.value !== '') {
        longitudeInput.required = true;
    } else if (longitudeInput.value !== '') {
        latitudeInput.required = true;
    } else {
        latitudeInput.required = false;
        longitudeInput.required = false;
    }
}

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                var latitudeInput = document.getElementById('latitude');
                var longitudeInput = document.getElementById('longitude');
                latitudeInput.value = position.coords.latitude;
                longitudeInput.value = position.coords.longitude;
                $('#advanced_filter').collapse('show'); 
                sendLocation(position);
            },
            function (error) {
                console.error("Error getting location:", error.message);
            }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

function sendLocation(position) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/update_location", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    var data = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude
    };
    xhr.send(JSON.stringify(data));
}
