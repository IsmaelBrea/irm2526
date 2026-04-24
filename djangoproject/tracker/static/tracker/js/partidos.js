document.addEventListener('DOMContentLoaded', function() {
    const leagueId = new URLSearchParams(window.location.search).get('league');
    const seasonFilter = document.getElementById('season-filter');
    const roundFilter = document.getElementById('round-filter');
    const matchesContainer = document.getElementById('matches-container');

    if (!leagueId) return;

    let seasonsLoaded = false;
    let roundsLoaded = false;
    let allMatches = [];

    function loadMatches() {
        const year = seasonFilter.value;
        const round = roundFilter.value;
        let url = `/tracker/api/league-matches/?league_id=${leagueId}`;
        if (year) url += `&year=${year}`;
        if (round) url += `&round=${round}`;

        fetch(url)
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success' && data.data.length > 0) {
                    allMatches = data.data;
                    
                    if (!seasonsLoaded) {
    const currentYear = new Date().getFullYear();
    const startYear = 2010;
    const years = [];
    
    for (let y = currentYear; y >= startYear; y--) {
        years.push(y);
    }
    
    seasonFilter.innerHTML = '';
    
    years.forEach(y => {
        const option = document.createElement('option');
        option.value = y;
        const prevYear = parseInt(y) - 1;
        option.textContent = `${prevYear}/${y}`;
        seasonFilter.appendChild(option);
    });
    
    seasonFilter.value = currentYear;
    seasonsLoaded = true;
}

                    const matchesInSeason = allMatches.filter(m => m.year === seasonFilter.value);
                    const totalRounds = Math.max(...matchesInSeason.map(m => parseInt(m.round)));
                    
                    if (!roundsLoaded || seasonFilter.value) {
                        roundFilter.innerHTML = '';
                        
                        for (let i = 1; i <= totalRounds; i++) {
                            const option = document.createElement('option');
                            option.value = i;
                            option.textContent = `${i}`;
                            roundFilter.appendChild(option);
                        }
                        
                        roundFilter.value = matchesInSeason[0].round;
                        roundsLoaded = true;
                    }

                    renderMatches(matchesInSeason);
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
        
        matches.forEach(match => {
            const matchDiv = document.createElement('div');
            matchDiv.className = 'bg-slate-900/50 border border-slate-800 rounded-lg p-4';
            const matchTime = `${match.hour}:${match.minute.toString().padStart(2, '0')}`;

            const score = match.local_goals !== 'x' 
                ? `${match.local_goals}-${match.visitor_goals}`
                : `${matchTime}`;
            
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
                    </div>
                </div>

                <div class="mt-2 text-slate-400 text-xs">J ${match.round}</div>
            `;
            
            matchesContainer.appendChild(matchDiv);
        });
    }

    seasonFilter.addEventListener('change', loadMatches);
    roundFilter.addEventListener('change', loadMatches);
    loadMatches();
});