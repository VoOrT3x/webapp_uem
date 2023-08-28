document.addEventListener("DOMContentLoaded", function () {
    var map = L.map('map').setView([-18.665695, 35.529562], 6);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18
    }).addTo(map);

    // Parse the GeoJSON data
    var districts = JSON.parse('{{ districts_json | safe }}');

    L.geoJSON(districts, {
        style: function (feature) {
            return {
                fillColor: '#ffff00',
                color: '#000000',
                weight: 1,
                fillOpacity: 0.4
            };
        },
        onEachFeature: function (feature, layer) {
            var popupContent = "<h3>" + feature.properties.ADM2_PT + "</h3>";
            popupContent += "<p>Additional information: " + feature.properties.ADM1_PT + "</p>";
            popupContent += "<a href='/map/district/" + feature.properties.ADM2_PT + "'><button>Go to " + feature.properties.ADM2_PT + "</button></a>";

            layer.bindPopup(popupContent);
        }
    }).addTo(map);
});
