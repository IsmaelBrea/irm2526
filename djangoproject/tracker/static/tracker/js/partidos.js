document.addEventListener('DOMContentLoaded', function() {
    const leagueId = new URLSearchParams(window.location.search).get('league');
    const seasonBtn = document.getElementById('btn-season');
    const roundBtn = document.getElementById('btn-round');
    const seasonDropdown = document.getElementById('dropdown-season');
    const roundDropdown = document.getElementById('dropdown-round');
    const seasonLabelText = document.getElementById('season-label-text');
    const roundLabelText = document.getElementById('round-label-text');
    const matchesContainer = document.getElementById('matches-container');

    if (!leagueId) return;

    let seasonsLoaded = false;
    let allMatches = [];
    let currentYear = new Date().getFullYear();
    let totalRoundsForSeason = 0; 



    function toggleDropdown(btn, dropdown) {
        btn.addEventListener('click', () => {
            dropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', (e) => {
            if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });
    }

function loadMatches(skipRoundFilter = false) {
    let url = `/tracker/api/league-matches/?league_id=${leagueId}`;
    
    if (seasonBtn.dataset.year) {
        url += `&year=${seasonBtn.dataset.year}`;
    }
    if (roundBtn.dataset.round && !skipRoundFilter) {
        url += `&round=${roundBtn.dataset.round}`;
    }

    fetch(url)
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success' && data.data.length > 0) {
                allMatches = data.data;

                // Si es carga inicial (sin year/round definidos)
                if (!seasonBtn.dataset.year && !roundBtn.dataset.round) {
                    const firstMatch = data.data[0];
                    seasonBtn.dataset.year = parseInt(firstMatch.year);
                    roundBtn.dataset.round = parseInt(firstMatch.round);
                    seasonLabelText.textContent = `${firstMatch.year - 1}/${firstMatch.year}`;
                    roundLabelText.textContent = `Jornada ${firstMatch.round}`;
                }
                
                if (!seasonsLoaded) {
                    const startYear = 2010;
                    const years = [];
                    
                    for (let y = currentYear; y >= startYear; y--) {
                        years.push(y);
                    }
                    
                    seasonDropdown.innerHTML = '';
                    years.forEach(y => {
                        const div = document.createElement('div');
                        const prevYear = y - 1;
                        div.className = 'px-4 py-2 text-xs text-slate-300 cursor-pointer hover:bg-slate-800 hover:text-green-500 transition-colors';
                        div.textContent = `${prevYear}/${y}`;
                        div.addEventListener('click', () => {
                            seasonBtn.dataset.year = y - 1;
                            seasonLabelText.textContent = `${prevYear}/${y}`;
                            seasonDropdown.classList.add('hidden');
                            roundDropdown.innerHTML = '';
                            loadMatches(true); 
                        });
                        seasonDropdown.appendChild(div);
                    });
                    
                    seasonLabelText.textContent = `${currentYear - 1}/${currentYear}`;
                    seasonsLoaded = true;
                }

                const matchesInSeason = allMatches.filter(m => parseInt(m.year) === parseInt(seasonBtn.dataset.year));
                
                if (matchesInSeason.length > 0) {
    
    if (skipRoundFilter) {
    totalRoundsForSeason = Math.max(...matchesInSeason.map(m => parseInt(m.round)));  // ✓ Encuentra la jornada más alta
        roundDropdown.innerHTML = ''; // Limpiar
        for (let i = 1; i <= totalRoundsForSeason; i++) {
            const div = document.createElement('div');
            div.className = 'px-4 py-2 text-xs text-slate-300 cursor-pointer hover:bg-slate-800 hover:text-green-500 transition-colors';
            div.textContent = `Jornada ${i}`;
            div.addEventListener('click', () => {
                roundBtn.dataset.round = i;
                roundLabelText.textContent = `Jornada ${i}`;
                roundDropdown.classList.add('hidden');
                loadMatches();
            });
            roundDropdown.appendChild(div);
        }
    }
    
// Buscar la jornada más cercana a la fecha actual
const today = new Date();
today.setHours(0, 0, 0, 0);

const roundDates = {};
matchesInSeason.forEach(m => {
    const round = parseInt(m.round);
    const matchDate = new Date(m.date);
    if (!roundDates[round] || matchDate < roundDates[round]) {
        roundDates[round] = matchDate;
    }
});

const sortedRounds = Object.keys(roundDates).sort((a, b) => {
    return Math.abs(roundDates[a] - today) - Math.abs(roundDates[b] - today);
});

const currentRound = parseInt(sortedRounds[0]);

// Solo actualizar en la primera carga, no cuando cambias de año
if (skipRoundFilter && !roundBtn.dataset.round) {
    roundBtn.dataset.round = currentRound;
    roundLabelText.textContent = `Jornada ${currentRound}`;
}

const matchesInRound = matchesInSeason.filter(m => parseInt(m.round) === parseInt(roundBtn.dataset.round));
renderMatches(matchesInRound);
} else {
                    matchesContainer.innerHTML = '<p class="text-slate-400">No hay partidos para esta temporada</p>';
                }
            } else {
                matchesContainer.innerHTML = '<p class="text-slate-400">No hay partidos disponibles</p>';
            }
        })
        .catch(e => {
            matchesContainer.innerHTML = `<p class="text-red-400">Error: ${e.message}</p>`;
        });
}

function renderMatches(matches) {
    matchesContainer.innerHTML = '';
    
    matches.forEach((match, index) => {
        const matchDiv = document.createElement('div');
        matchDiv.className = 'bg-slate-900/50 border border-slate-800 rounded-lg p-4 mb-4';
        const matchTime = `${match.hour}:${match.minute.toString().padStart(2, '0')}`;
        const uniqueId = `odds-${index}-${match.id}`;

        const score = match.local_goals !== 'x' 
            ? `${match.local_goals}-${match.visitor_goals}`
            : `${matchTime}`;

const oddsButton = match.odds && Array.isArray(match.odds) && match.odds.length > 0
    ? `<span class="w-px bg-slate-700"></span>
       <button class="ml-3 px-4 py-3 text-sm font-semibold text-green-400 hover:text-slate-100 border border-green-600 hover:border-slate-400 rounded transition odds-toggle" data-odds-id="${uniqueId}">
        Ver Cuotas
       </button>`
    : '';

        // HTML de cuotas (oculto por defecto)
        let oddsHtml = '';
        if (match.odds && Array.isArray(match.odds) && match.odds.length > 0) {
            oddsHtml = `
                <div id="${uniqueId}" class="hidden mt-4 pt-4 border-t border-slate-700">
                    ${match.odds.map(odd => `
                        <div class="mb-3 pb-3 border-b border-slate-800 last:border-b-0">
                            <p class="text-slate-400 text-xs mb-2">${odd.bookmaker}</p>
                            <div class="flex justify-between gap-2 text-xs">
                                <span class="flex-1">
                                    <strong class="text-green-400">${match.local}</strong>: ${odd.home.toFixed(2)}
                                </span>
                                <span class="flex-1 text-center">
                                    <strong class="text-orange-400">Empate</strong>: ${odd.draw.toFixed(2)}
                                </span>
                                <span class="flex-1 text-right">
                                    <strong class="text-blue-400">${match.visitor}</strong>: ${odd.away.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        matchDiv.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center gap-3 flex-1">
                    ${match.local_shield ? `<img src="${match.local_shield}" class="w-8 h-8 object-contain">` : '<div class="w-8 h-8"></div>'}
                    <div class="flex-1">
                        <p class="text-white font-semibold text-sm">${match.local}</p>
                    </div>
                </div>

                <div class="text-center px-6">
                    <p class="text-white font-bold text-lg">${score}</p>
                    <p class="text-slate-400 text-xs">
                        ${match.local_goals !== 'x' ? `${match.date} - ${matchTime}` : match.date}
                    </p>
                </div>

                <div class="flex items-center gap-3 flex-1 justify-end">
                    <div class="flex-1 text-right">
                        <p class="text-white font-semibold text-sm">${match.visitor}</p>
                    </div>
                    ${match.visitor_shield ? `<img src="${match.visitor_shield}" class="w-8 h-8 object-contain">` : '<div class="w-8 h-8"></div>'}
                    ${oddsButton}
                </div>
            </div>

            <div class="mt-2 text-slate-400 text-xs">J ${match.round}</div>
            ${oddsHtml}
        `;
            
        matchesContainer.appendChild(matchDiv);
    });

    // Añadir event listeners para los botones de cuotas
    document.querySelectorAll('.odds-toggle').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const oddsId = btn.getAttribute('data-odds-id');
            const oddsContainer = document.getElementById(oddsId);
            if (oddsContainer) {
                oddsContainer.classList.toggle('hidden');
                btn.textContent = oddsContainer.classList.contains('hidden') 
                    ? 'Ver Cuotas' 
                    : 'Ocultar Cuotas';
            }
        });
    });
}

    toggleDropdown(seasonBtn, seasonDropdown);
toggleDropdown(roundBtn, roundDropdown);

// Inicializar temporada antes de cargar
seasonBtn.dataset.year = currentYear - 1;
seasonLabelText.textContent = `${currentYear - 1}/${currentYear}`;

loadMatches(true);
});