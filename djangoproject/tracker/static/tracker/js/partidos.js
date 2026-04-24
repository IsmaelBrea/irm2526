document.addEventListener('DOMContentLoaded', function() {
    const leagueId = new URLSearchParams(window.location.search).get('league');
    const roundFilter = document.getElementById('round-filter');
    const matchesContainer = document.getElementById('matches-container');

    if (!leagueId) return;

    function loadMatches() {
        const round = roundFilter.value;
        let url = `/tracker/api/league-matches/?league_id=${leagueId}`;
        if (round) url += `&round=${round}`;

        fetch(url)
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success' && data.data.length > 0) {
                    const matches = data.data;
                    
                    if (!round && roundFilter.children.length === 0) {
                        const totalRounds = parseInt(matches[0].total_rounds) || 38;
                        const currentRound = matches[0].round;
                        
                        
                        for (let i = 1; i <= totalRounds; i++) {
                            const option = document.createElement('option');
                            option.value = i;
                            option.textContent = `Jornada ${i}`;
                            roundFilter.appendChild(option);
                        }
                        
                        roundFilter.value = currentRound;
                    }

                    renderMatches(matches);
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

    roundFilter.addEventListener('change', loadMatches);
    loadMatches();
});