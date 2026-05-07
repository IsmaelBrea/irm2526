// Función global de inicialización
window.initMap = function() {
    const coordsData = document.getElementById('team-coords-data');
    if (!coordsData) return;

    let teamCoords;
    try {
        teamCoords = JSON.parse(coordsData.textContent);
    } catch (e) {
        console.error("Error al leer coordenadas:", e);
        return;
    }

    const mapElement = document.getElementById('map');
    const statusOverlay = document.getElementById('map-status');

    if (!mapElement || !teamCoords || !teamCoords.lat) {
        if (statusOverlay) statusOverlay.classList.remove('hidden');
        return;
    }

    if (statusOverlay) statusOverlay.classList.add('hidden');

    // Inicializar mapa
    const map = new google.maps.Map(mapElement, {
        center: teamCoords,
        zoom: 15,
        styles: [
            { "elementType": "geometry", "stylers": [{ "color": "#0f172a" }] },
            { "elementType": "labels.text.fill", "stylers": [{ "color": "#94a3b8" }] },
            { "elementType": "labels.text.stroke", "stylers": [{ "color": "#0f172a" }] },
            { "featureType": "road", "elementType": "geometry", "stylers": [{ "color": "#1e293b" }] },
            { "featureType": "water", "elementType": "geometry", "stylers": [{ "color": "#020617" }] }
        ],
        disableDefaultUI: true
    });

    // Marcador
    new google.maps.Marker({
        position: teamCoords,
        map: map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 8,
            fillColor: "#22c55e",
            fillOpacity: 1,
            strokeWeight: 2,
            strokeColor: "#ffffff"
        }
    });
};

// Lógica de Interfaz
document.addEventListener('DOMContentLoaded', function() {
    const btnDropdown = document.getElementById('btn-open-dropdown');
    const dropdown = document.getElementById('team-dropdown');
    const searchInput = document.getElementById('search-team');
    const btnAnalizar = document.getElementById('btn-analizar');
    const hiddenIdInput = document.getElementById('selected-team-id');

    if (!btnDropdown || !dropdown) return;

    btnDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase();
        if (val.length > 0) dropdown.classList.remove('hidden');
        dropdown.querySelectorAll('.team-option').forEach(opt => {
            const name = opt.dataset.name.toLowerCase();
            opt.style.display = name.includes(val) ? 'flex' : 'none';
        });
    });

    dropdown.querySelectorAll('.team-option').forEach(opt => {
        opt.addEventListener('click', function() {
            hiddenIdInput.value = this.dataset.id;
            searchInput.value = this.dataset.name;
            document.getElementById('display-selected').innerHTML = `<span class="text-green-500 font-black">${this.dataset.name}</span>`;
            dropdown.classList.add('hidden');
        });
    });

    btnAnalizar.addEventListener('click', function() {
        const teamId = hiddenIdInput.value;
        if (!teamId) return alert("Selecciona un equipo");
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('team', teamId);
        btnAnalizar.innerHTML = "CARGANDO...";
        window.location.search = urlParams.toString();
    });

    document.addEventListener('click', () => dropdown.classList.add('hidden'));
});