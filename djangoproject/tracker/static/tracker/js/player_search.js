document.addEventListener('DOMContentLoaded', function() {
    const playersData = document.getElementById('playersData');
    if (!playersData) return;
    
    const players = JSON.parse(playersData.textContent);
    const searchInput = document.getElementById('player-search');
    const teamFilter = document.getElementById('team-filter');
    const dropdown = document.getElementById('player-dropdown');
    const statsContainer = document.getElementById('stats-container');
    const infoContainer = document.getElementById('info-container');

    // Llenar select de equipos únicos
    const uniqueTeams = [...new Set(players.map(p => p.team_name))].sort();
    uniqueTeams.forEach(team => {
        const option = document.createElement('option');
        option.value = team;
        option.textContent = team;
        teamFilter.appendChild(option);
    });

    function filterPlayers() {
        const query = searchInput.value.toLowerCase();
        const selectedTeam = teamFilter.value;
        dropdown.innerHTML = '';

        // Si no hay búsqueda y no hay equipo seleccionado, ocultar
        if (query.length < 1 && !selectedTeam) {
            dropdown.classList.add('hidden');
            return;
        }

        let filtered = players;

        // Filtrar por equipo si está seleccionado
        if (selectedTeam) {
            filtered = filtered.filter(p => p.team_name === selectedTeam);
        }

        // Filtrar por búsqueda si hay texto
        if (query.length > 0) {
            filtered = filtered.filter(p => p.name.toLowerCase().includes(query));
        }


        if (filtered.length === 0) {
            dropdown.innerHTML = '<div class="p-4 text-slate-500">No hay resultados</div>';
        } else {
            filtered.forEach(player => {
                const option = document.createElement('div');
                option.className = 'p-4 hover:bg-slate-800 cursor-pointer border-b border-slate-800 last:border-b-0 flex items-center gap-2';
                
                const crest = player.team_crest 
                    ? `<img src="${player.team_crest}" class="w-5 h-5 object-contain">` 
                    : '';
                
                option.innerHTML = `
                    ${crest}
                    <div>
                        <p class="text-white font-semibold text-sm">${player.name}</p>
                        <p class="text-slate-400 text-xs">${player.position || 'N/A'} • ${player.team_name}</p>
                    </div>
                `;
                
                option.addEventListener('click', () => selectPlayer(player));
                dropdown.appendChild(option);
            });
        }

        dropdown.classList.remove('hidden');
    }

    function selectPlayer(player) {
    searchInput.value = player.name;
    dropdown.classList.add('hidden');

    // Llenar información
    document.getElementById('info-name').textContent = `${player.firstName || ''} ${player.lastName || player.name}`.trim();
    document.getElementById('info-dob').textContent = player.dateOfBirth || 'N/A';
    document.getElementById('info-position').textContent = player.position || 'N/A';
    document.getElementById('info-nationality').textContent = player.nationality || 'N/A';
    document.getElementById('info-team').textContent = player.team_name || 'N/A';

    statsContainer.classList.remove('hidden');
    infoContainer.classList.remove('hidden');
}

        // Focus en el input activa el filtro aunque esté vacío
    searchInput.addEventListener('focus', filterPlayers);
    searchInput.addEventListener('input', filterPlayers);
    teamFilter.addEventListener('change', function() {
        dropdown.classList.add('hidden'); // Solo cierra el dropdown, no lo abre
        searchInput.value = ''; // Limpia el buscador también (opcional)
    });

    document.addEventListener('click', function(e) {
        if (e.target !== searchInput && e.target !== dropdown && e.target !== teamFilter) {
            dropdown.classList.add('hidden');
        }
    });
});