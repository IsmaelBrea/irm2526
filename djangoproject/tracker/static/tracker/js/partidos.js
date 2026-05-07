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

    // ── POPUP DE CUOTAS ──
    const popup = document.createElement('div');
    popup.innerHTML = `
        <div id="odds-backdrop" class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm hidden"></div>
        <div id="odds-modal" class="fixed z-50 hidden top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md px-4">
            <div class="bg-slate-900 border border-slate-700 rounded-[2rem] shadow-2xl overflow-hidden">
                <div class="bg-slate-800/60 px-6 py-5 border-b border-slate-700 flex items-center justify-between">
                    <div>
                        <p id="popup-teams" class="text-white font-black text-sm uppercase tracking-wide"></p>
                        <p id="popup-date" class="text-slate-500 font-mono text-[10px] mt-0.5"></p>
                    </div>
                    <button id="popup-close" class="w-8 h-8 flex items-center justify-center rounded-xl bg-slate-700 hover:bg-slate-600 text-slate-300 hover:text-white transition-all text-lg font-bold">×</button>
                </div>
                <div id="popup-odds-body" class="p-6 space-y-4 max-h-[60vh] overflow-y-auto"></div>
            </div>
        </div>
    `;
    document.body.appendChild(popup);

    const backdrop = document.getElementById('odds-backdrop');
    const modal    = document.getElementById('odds-modal');
    const closeBtn = document.getElementById('popup-close');

    function openOddsPopup(match) {
        document.getElementById('popup-teams').textContent = `${match.local} vs ${match.visitor}`;
        document.getElementById('popup-date').textContent  = match.date;

        const body = document.getElementById('popup-odds-body');
        body.innerHTML = match.odds.map(odd => `
            <div class="bg-slate-800/50 border border-slate-700/50 rounded-2xl p-4">
                <p class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-3">${odd.bookmaker}</p>
                <div class="grid grid-cols-3 gap-3 text-center">
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/30">
                        <p class="text-[9px] text-slate-500 uppercase font-mono mb-1">${match.local}</p>
                        <p class="text-green-400 font-black text-lg">${odd.home.toFixed(2)}</p>
                    </div>
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/30">
                        <p class="text-[9px] text-slate-500 uppercase font-mono mb-1">Empate</p>
                        <p class="text-amber-400 font-black text-lg">${odd.draw.toFixed(2)}</p>
                    </div>
                    <div class="bg-slate-900/80 rounded-xl p-3 border border-slate-700/30">
                        <p class="text-[9px] text-slate-500 uppercase font-mono mb-1">${match.visitor}</p>
                        <p class="text-blue-400 font-black text-lg">${odd.away.toFixed(2)}</p>
                    </div>
                </div>
            </div>
        `).join('');

        backdrop.classList.remove('hidden');
        modal.classList.remove('hidden');
    }

    function closeOddsPopup() {
        backdrop.classList.add('hidden');
        modal.classList.add('hidden');
    }

    closeBtn.addEventListener('click', closeOddsPopup);
    backdrop.addEventListener('click', closeOddsPopup);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeOddsPopup(); });

    // ── DROPDOWNS ──
    function toggleDropdown(btn, dropdown) {
        btn.addEventListener('click', () => dropdown.classList.toggle('hidden'));
        document.addEventListener('click', (e) => {
            if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
                dropdown.classList.add('hidden');
            }
        });
    }

    // ── CARGA DE PARTIDOS ──
    function loadMatches(skipRoundFilter = false) {
        let url = `/tracker/api/league-matches/?league_id=${leagueId}`;
        if (seasonBtn.dataset.year)                     url += `&year=${seasonBtn.dataset.year}`;
        if (roundBtn.dataset.round && !skipRoundFilter) url += `&round=${roundBtn.dataset.round}`;

        fetch(url)
            .then(r => r.json())
            .then(data => {
                if (data.status === 'success' && data.data.length > 0) {
                    allMatches = data.data;

                    if (!seasonBtn.dataset.year && !roundBtn.dataset.round) {
                        const firstMatch = data.data[0];
                        seasonBtn.dataset.year = parseInt(firstMatch.year);
                        roundBtn.dataset.round = parseInt(firstMatch.round);
                        seasonLabelText.textContent = `${firstMatch.year - 1}/${firstMatch.year}`;
                        roundLabelText.textContent  = `Jornada ${firstMatch.round}`;
                    }

                    if (!seasonsLoaded) {
                        const years = [];
                        for (let y = currentYear; y >= 2010; y--) years.push(y);

                        seasonDropdown.innerHTML = '';
                        years.forEach(y => {
                            const div = document.createElement('div');
                            div.className = 'px-4 py-2 text-xs text-slate-300 cursor-pointer hover:bg-slate-800 hover:text-green-500 transition-colors';
                            div.textContent = `${y - 1}/${y}`;
                            div.addEventListener('click', () => {
                                seasonBtn.dataset.year = y - 1;
                                seasonLabelText.textContent = `${y - 1}/${y}`;
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
                            totalRoundsForSeason = Math.max(...matchesInSeason.map(m => parseInt(m.round)));
                            roundDropdown.innerHTML = '';
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

                        const today = new Date();
                        today.setHours(0, 0, 0, 0);
                        const roundDates = {};
                        matchesInSeason.forEach(m => {
                            const round = parseInt(m.round);
                            const matchDate = new Date(m.date);
                            if (!roundDates[round] || matchDate < roundDates[round]) roundDates[round] = matchDate;
                        });
                        const sortedRounds = Object.keys(roundDates).sort((a, b) =>
                            Math.abs(roundDates[a] - today) - Math.abs(roundDates[b] - today)
                        );
                        const currentRound = parseInt(sortedRounds[0]);

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

    // ── RENDER PARTIDOS ──
    function renderMatches(matches) {
        matchesContainer.innerHTML = '';

        matches.forEach((match) => {
            const matchDiv = document.createElement('div');
            matchDiv.className = 'bg-slate-900/50 border border-slate-800 rounded-2xl p-5 transition-all hover:border-slate-700';

            const matchTime = `${match.hour}:${match.minute.toString().padStart(2, '0')}`;
            const score = match.local_goals !== 'x'
                ? `${match.local_goals} - ${match.visitor_goals}`
                : matchTime;

            const hasOdds = match.odds && Array.isArray(match.odds) && match.odds.length > 0;

            matchDiv.innerHTML = `
                <div class="flex items-center justify-between gap-4">

                    <div class="flex items-center gap-3 flex-1 min-w-0">
                        ${match.local_shield
                            ? `<img src="${match.local_shield}" class="w-9 h-9 object-contain flex-shrink-0">`
                            : '<div class="w-9 h-9"></div>'}
                        <p class="text-white font-bold text-sm truncate">${match.local}</p>
                    </div>

                    <div class="text-center flex-shrink-0 px-4">
                        <p class="text-white font-black text-xl tracking-widest">${score}</p>
                        <p class="text-slate-500 text-[10px] font-mono mt-0.5">${match.date}</p>
                        <p class="text-slate-600 text-[9px] font-mono uppercase">J${match.round}</p>
                    </div>

                    <div class="flex items-center gap-3 flex-1 min-w-0 justify-end">
                        <p class="text-white font-bold text-sm truncate text-right">${match.visitor}</p>
                        ${match.visitor_shield
                            ? `<img src="${match.visitor_shield}" class="w-9 h-9 object-contain flex-shrink-0">`
                            : '<div class="w-9 h-9"></div>'}
                        ${hasOdds ? `
                        <button class="odds-btn flex-shrink-0 px-3 py-2 text-[9px] font-black uppercase tracking-widest text-green-500 border border-green-500/30 bg-green-500/5 rounded-xl hover:bg-green-500/10 hover:border-green-500/60 transition-all whitespace-nowrap">
                            Ver Cuotas
                        </button>` : ''}
                    </div>

                </div>
            `;

            if (hasOdds) {
                matchDiv.querySelector('.odds-btn').addEventListener('click', () => openOddsPopup(match));
            }

            matchesContainer.appendChild(matchDiv);
        });
    }

    toggleDropdown(seasonBtn, seasonDropdown);
    toggleDropdown(roundBtn, roundDropdown);

    seasonBtn.dataset.year = currentYear - 1;
    seasonLabelText.textContent = `${currentYear - 1}/${currentYear}`;

    loadMatches(true);
});