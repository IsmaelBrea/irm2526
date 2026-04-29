document.addEventListener('DOMContentLoaded', function() {
    const btnDropdown = document.getElementById('btn-open-dropdown');
    const dropdown = document.getElementById('team-dropdown');
    const searchInput = document.getElementById('search-team');
    const btnAnalizar = document.getElementById('btn-analizar');
    const hiddenIdInput = document.getElementById('selected-team-id');
    const display = document.getElementById('display-selected');
    
    if (!btnDropdown || !dropdown) return;

    const options = dropdown.querySelectorAll('.team-option');

    // 1. Abrir/Cerrar dropdown
    btnDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    // 2. Filtrar equipos
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.toLowerCase();
        if (val.length > 0) dropdown.classList.remove('hidden');

        options.forEach(opt => {
            const name = opt.dataset.name.toLowerCase();
            opt.style.display = name.includes(val) ? 'flex' : 'none';
        });
    });

    // 3. SELECCIONAR (Ahora solo rellena el campo, no recarga)
    options.forEach(opt => {
        opt.addEventListener('click', function() {
            const teamId = this.dataset.id;
            const teamName = this.dataset.name;
            
            searchInput.value = teamName;
            hiddenIdInput.value = teamId; // Guardamos el ID internamente
            
            display.innerText = teamName;
            display.classList.add('text-green-500', 'border-green-500/30');
            
            dropdown.classList.add('hidden');
        });
    });

    // 4. ACCIÓN DEL BOTÓN ANALIZAR (Aquí es donde ocurre la recarga)
    btnAnalizar.addEventListener('click', function() {
        const teamId = hiddenIdInput.value;
        
        if (!teamId) {
            alert("Por favor, selecciona un equipo de la lista antes de analizar.");
            return;
        }

        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('team', teamId);
        
        // Efecto visual de carga
        btnAnalizar.innerHTML = "CARGANDO...";
        btnAnalizar.disabled = true;
        
        window.location.search = urlParams.toString();
    });

    // Cerrar si clic fuera
    document.addEventListener('click', (e) => {
        if (!btnDropdown.contains(e.target) && !dropdown.contains(e.target) && !searchInput.contains(e.target)) {
            dropdown.classList.add('hidden');
        }
    });
});