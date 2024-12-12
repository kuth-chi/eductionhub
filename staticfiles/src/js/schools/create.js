const map = L.map('map').setView([11.5564, 104.9282], 14);
const tileLayers = {
    "Light Mode": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }),
    "Dark Mode": L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap contributors © CARTO'
    }),
    "Satellite": L.tileLayer('https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', {
        subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
        attribution: '© Google Maps'
    })
};

tileLayers["Light Mode"].addTo(map);

let marker = null;

function updateMarker() {
    const locationInput = document.getElementById('id_location').value.trim();
    const nameInput = document.getElementById('id_name').value.trim();
    const coords = locationInput.split(',').map(coord => parseFloat(coord));
    
    if (coords.length === 2 && !isNaN(coords[0]) && !isNaN(coords[1])) {
        const [lat, lng] = coords;
        
        if (lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180) {
            if (marker) {
                marker.setLatLng([lat, lng]);
            } else {
                marker = L.marker([lat, lng], { draggable: true }).addTo(map);
                
                marker.on('dragend', function (e) {
                    const newCoords = e.target.getLatLng();
                    const newLat = newCoords.lat.toFixed(6);
                    const newLng = newCoords.lng.toFixed(6);
                    
                    document.getElementById('id_location').value = `${newLat},${newLng}`;
                    
                    const updatedPopupContent = `<b>${nameInput || 'Unnamed Marker'}</b><br>Lat: ${newLat}, Lng: ${newLng}`;
                    marker.bindPopup(updatedPopupContent).openPopup();
                });
            }

            const popupContent = `<b>${nameInput || 'Unnamed Marker'}</b><br>Lat: ${lat}, Lng: ${lng}`;
            marker.bindPopup(popupContent).openPopup();
            map.setView([lat, lng], 13);
        }
    }
}

document.getElementById('id_location').addEventListener('input', updateMarker);
document.getElementById('id_name').addEventListener('input', updateMarker);

const layoutSelector = document.createElement('select');

const tileIcons = {
    "Light Mode": "bi-sun",
    "Dark Mode": "bi-moon",
    "Satellite": "bi-globe"
};

layoutSelector.style.position = 'absolute';
layoutSelector.style.top = '10px';
layoutSelector.style.right = '10px';
layoutSelector.style.zIndex = '1000';
layoutSelector.style.padding = '5px';
layoutSelector.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
layoutSelector.style.borderRadius = '5px';

for (const [name, layer] of Object.entries(tileLayers)) {
    const option = document.createElement('option');
    option.value = name;
    option.innerHTML = `<i class="bi ${tileIcons[name]}" style="margin-right: 8px;"></i> ${name}`;
    layoutSelector.appendChild(option);
}

layoutSelector.addEventListener('change', function () {
    for (const layer of Object.values(tileLayers)) {
        map.removeLayer(layer);
    }
    tileLayers[layoutSelector.value].addTo(map);
});
document.getElementById('map').appendChild(layoutSelector);
