document.addEventListener('DOMContentLoaded', function() {
    const playersData = document.getElementById('playersData');
    if (!playersData) return;
    
    const players = JSON.parse(playersData.textContent);
    const searchInput = document.getElementById('player-search');
    const teamFilter = document.getElementById('team-filter');
    const dropdown = document.getElementById('player-dropdown');
    const competitionsContainer = document.getElementById('competitions-container');
    const infoContainer = document.getElementById('info-container');

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
                        <p class="text-slate-400 text-xs">${player.position || 'N/A'} - ${player.team_name}</p>
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
    document.getElementById('info-dob').textContent = player.dateOfBirth || '-';
    document.getElementById('info-position').textContent = player.position || '-';
    document.getElementById('info-nationality').textContent = player.nationality || '-';
    document.getElementById('info-team').textContent = player.team_name || '-';
    
    const crestDiv = document.getElementById('info-team-crest');
    const crest = player.team_crest 
        ? `<img src="${player.team_crest}" class="w-6 h-6 object-contain">` 
        : '';
    crestDiv.innerHTML = crest;

    competitionsContainer.classList.remove('hidden');
    infoContainer.classList.remove('hidden');

    const competitionsList = document.getElementById('competitions-list');
    competitionsList.innerHTML = '<p class="text-slate-400">Cargando...</p>';

    if (!player.id) {
    competitionsList.innerHTML = `<p class="text-red-400">Sin ID - Propiedades: ${Object.keys(player).join(', ')}</p>`;
    return;
}

    fetch(`/tracker/api/player-stats/?player_id=${player.id}`)
    .then(r => {
        competitionsList.innerHTML = `<p>Status: ${r.status}</p>`;
        return r.json();
    })
    .then(data => {
        competitionsList.innerHTML = `
            <p>Data recibida: ${JSON.stringify(data).substring(0, 100)}</p>
            <p>Status: ${data.status}</p>
            <p>CurrentTeam: ${data.data?.currentTeam ? 'existe' : 'NO existe'}</p>
            <p>Competiciones: ${data.data?.currentTeam?.runningCompetitions ? data.data.currentTeam.runningCompetitions.length : 'NO existe'}</p>
        `;
        
        if (data.status === 'success' && data.data.currentTeam && data.data.currentTeam.runningCompetitions) {
            const competitions = data.data.currentTeam.runningCompetitions;
            competitionsList.innerHTML = '';
            
            competitions.forEach(comp => {
                const item = document.createElement('div');
                item.className = 'bg-slate-800/50 p-4 rounded flex items-center gap-4';
                item.innerHTML = `
                    <div class="bg-white rounded p-2 flex items-center justify-center w-12 h-12 flex-shrink-0">
                        ${comp.emblem ? `<img src="${comp.emblem}" class="w-8 h-8 object-contain">` : '<span class="w-8 h-8"></span>'}
                    </div>
                    <div>
                        <p class="text-white font-semibold text-base">${comp.name}</p>
                        <p class="text-slate-400 text-sm">${comp.type}</p>
                    </div>
                `;
                competitionsList.appendChild(item);
            });
        } else {
            competitionsList.innerHTML = '<p class="text-slate-400">Sin competiciones</p>';
        }
    })
    .catch(e => {
        competitionsList.innerHTML = `<p class="text-red-400">Error: ${e.message}</p>`;
    });
}


    searchInput.addEventListener('focus', filterPlayers);
    searchInput.addEventListener('input', filterPlayers);
    teamFilter.addEventListener('change', function() {
        dropdown.classList.add('hidden'); 
        searchInput.value = '';
    });

    document.addEventListener('click', function(e) {
        if (e.target !== searchInput && e.target !== dropdown && e.target !== teamFilter) {
            dropdown.classList.add('hidden');
        }
    });
});