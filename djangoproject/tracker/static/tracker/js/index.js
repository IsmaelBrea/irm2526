const styleSheet = document.createElement("style");
styleSheet.textContent = `
    @keyframes fadeInRight {
        from { opacity: 0; transform: translateX(15px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    .team-dropdown::-webkit-scrollbar { width: 3px; }
    .team-dropdown::-webkit-scrollbar-thumb { background: #334155; border-radius: 10px; }
`;
document.head.appendChild(styleSheet);

// Configuración base compartida para todos los gráficos Plotly
const PLOTLY_BASE_LAYOUT = {
    paper_bgcolor: 'transparent',
    plot_bgcolor:  'transparent',
    font:          { color: '#94a3b8', family: 'monospace', size: 10 },
    margin:        { t: 10, r: 10, b: 40, l: 40 },
    showlegend:    true,
    legend:        { orientation: 'h', y: -0.25, font: { size: 9 } },
    xaxis: { gridcolor: '#1e293b', linecolor: '#334155', tickfont: { size: 9, color: '#64748b' }, zeroline: false },
    yaxis: { gridcolor: '#1e293b', linecolor: '#334155', tickfont: { size: 9, color: '#64748b' }, zeroline: false },
};

const PLOTLY_CONFIG = { displayModeBar: false, responsive: true };

document.addEventListener('DOMContentLoaded', function () {

    // Leer preselect de la URL ANTES de cualquier reset
    const urlParams = new URLSearchParams(window.location.search);
    const preselectId = urlParams.get('preselect');

    const resetSelectors = () => {
        ['search-local', 'search-visitor'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });

        ['select-local', 'select-visitor'].forEach(id => {
            const el = document.getElementById(id);
            if (!el) return;
            // Solo preservar select-local si hay preselect en URL
            if (id === 'select-local' && preselectId) return;
            el.value = '';
        });

        ['display-local', 'display-visitor'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = '[ SIN SELECCIÓN ]';
                el.className = "h-14 border border-dashed border-slate-800 rounded-[1.2rem] flex items-center justify-center text-slate-500 text-[10px] uppercase font-mono px-6 text-center transition-all duration-300";
            }
        });

        const container = document.getElementById('results-container');
        if (container) container.classList.add('hidden');
    };

    resetSelectors();

    // Setup (solo una vez cada uno)
    setupDropdown('btn-open-local',   'dropdown-local',   'select-local',   'display-local',   'search-local');
    setupDropdown('btn-open-visitor', 'dropdown-visitor', 'select-visitor', 'display-visitor', 'search-visitor');
    setupFilter('search-local',   'dropdown-local');
    setupFilter('search-visitor', 'dropdown-visitor');

    // PRE-SELECCIÓN usando el ID de la URL directamente
    if (preselectId) {
        const option = document.querySelector(`#dropdown-local .team-option[data-id="${preselectId}"]`);
        if (option) {
            const name  = option.dataset.name;
            const crest = option.dataset.crest;

            // Actualizar el input hidden
            document.getElementById('select-local').value = preselectId;
            // Actualizar el buscador
            document.getElementById('search-local').value = name;
            // Actualizar el display
            const display = document.getElementById('display-local');
            display.innerHTML = crest
                ? `<img src="${crest}" class="w-8 h-8 object-contain mr-3"><span>${name}</span>`
                : `<span>${name}</span>`;
            display.className = "h-14 border border-dashed border-green-500/40 bg-green-500/5 rounded-[1.2rem] flex items-center justify-center text-green-500 text-xs font-black uppercase font-mono px-6 text-center shadow-inner gap-2";
        }
    }


    // ── DROPDOWN CUSTOM (botón +) ──
    function setupDropdown(btnId, dropdownId, hiddenInputId, displayId, searchInputId) {
        const btn       = document.getElementById(btnId);
        const dropdown  = document.getElementById(dropdownId);
        const hidden    = document.getElementById(hiddenInputId);
        const display   = document.getElementById(displayId);
        const searchInp = document.getElementById(searchInputId);

        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            document.querySelectorAll('.team-dropdown').forEach(d => {
                if (d !== dropdown) d.classList.add('hidden');
            });
            dropdown.classList.toggle('hidden');
        });

        dropdown.querySelectorAll('.team-option').forEach(option => {
            option.addEventListener('click', function () {
                const id    = this.dataset.id;
                const name  = this.dataset.name;
                const crest = this.dataset.crest;

                const otherSearch = hiddenInputId === 'select-local' ? 'search-visitor' : 'search-local';
                const otherName   = document.getElementById(otherSearch).value;

                if (name === otherName) {
                    alert("No puedes seleccionar el mismo equipo.");
                    return;
                }

                hidden.value    = id;
                searchInp.value = name;
                display.innerHTML = crest
                    ? `<img src="${crest}" class="w-8 h-8 object-contain mr-3" alt="${name}"><span>${name}</span>`
                    : `<span>${name}</span>`;
                display.className = "h-14 border border-dashed border-green-500/40 bg-green-500/5 rounded-[1.2rem] flex items-center justify-center text-green-500 text-xs font-black uppercase font-mono px-6 text-center shadow-inner gap-2";
                dropdown.classList.add('hidden');
            });
        });

        document.addEventListener('click', function (e) {
            if (!dropdown.contains(e.target) && e.target !== btn) {
                dropdown.classList.add('hidden');
            }
        });
    }

    setupDropdown('btn-open-local',   'dropdown-local',   'select-local',   'display-local',   'search-local');
    setupDropdown('btn-open-visitor', 'dropdown-visitor', 'select-visitor', 'display-visitor', 'search-visitor');

    // ── FILTRO DINÁMICO EN INPUT DE BÚSQUEDA ──
    function setupFilter(inputId, dropdownId) {
        const input    = document.getElementById(inputId);
        const dropdown = document.getElementById(dropdownId);
        const options  = Array.from(dropdown.querySelectorAll('.team-option'));

        input.addEventListener('input', function () {
            const term = input.value.toLowerCase();
            options.forEach(opt => {
                opt.style.display = opt.dataset.name.toLowerCase().includes(term) ? '' : 'none';
            });
            if (term.length > 0) dropdown.classList.remove('hidden');
            else dropdown.classList.add('hidden');
        });
    }

    setupFilter('search-local',   'dropdown-local');
    setupFilter('search-visitor', 'dropdown-visitor');

    // ── BOTÓN REVERSE ──
    document.getElementById('btn-reverse').addEventListener('click', function () {
        const lInp  = document.getElementById('search-local'),   vInp  = document.getElementById('search-visitor');
        const lSel  = document.getElementById('select-local'),   vSel  = document.getElementById('select-visitor');
        const lDisp = document.getElementById('display-local'),  vDisp = document.getElementById('display-visitor');

        [lInp.value,      vInp.value]      = [vInp.value,      lInp.value];
        [lSel.value,      vSel.value]      = [vSel.value,      lSel.value];
        [lDisp.innerHTML, vDisp.innerHTML] = [vDisp.innerHTML, lDisp.innerHTML];
        [lDisp.className, vDisp.className] = [vDisp.className, lDisp.className];
    });

    // ── GRÁFICO DE LÍNEAS: forma últimos 5 partidos ──
    function renderFormChart(formA, formB, nameA, nameB) {
        const traceA = {
            x: formA.map(d => d.jornada), y: formA.map(d => d.pts), name: nameA,
            mode: 'lines+markers',
            line:   { color: '#22c55e', width: 2.5, shape: 'spline' },
            marker: { color: '#22c55e', size: 7, symbol: 'circle' },
            text:   formA.map(d => `vs ${d.rival}<br>${d.score}`),
            hovertemplate: '<b>%{text}</b><br>Puntos: %{y}<extra></extra>',
        };
        const traceB = {
            x: formB.map(d => d.jornada), y: formB.map(d => d.pts), name: nameB,
            mode: 'lines+markers',
            line:   { color: '#3b82f6', width: 2.5, shape: 'spline' },
            marker: { color: '#3b82f6', size: 7, symbol: 'circle' },
            text:   formB.map(d => `vs ${d.rival}<br>${d.score}`),
            hovertemplate: '<b>%{text}</b><br>Puntos: %{y}<extra></extra>',
        };
        const layout = {
            ...PLOTLY_BASE_LAYOUT,
            yaxis: { ...PLOTLY_BASE_LAYOUT.yaxis, tickvals: [0, 1, 3], ticktext: ['Derrota (0)', 'Empate (1)', 'Victoria (3)'], range: [-0.3, 3.5] },
        };
        Plotly.newPlot('chart-form', [traceA, traceB], layout, PLOTLY_CONFIG);
    }

    // ── GRÁFICO DE BARRAS: métricas comparativas ──
    function renderBarChart(barMetrics, nameA, nameB) {
        const labels = barMetrics.map(d => d.metrica);
        const traceA = {
            x: labels, y: barMetrics.map(d => d.val_a), name: nameA, type: 'bar',
            marker: { color: 'rgba(34,197,94,0.75)', line: { color: '#22c55e', width: 1 } },
            hovertemplate: '%{y}<extra></extra>',
        };
        const traceB = {
            x: labels, y: barMetrics.map(d => d.val_b), name: nameB, type: 'bar',
            marker: { color: 'rgba(59,130,246,0.75)', line: { color: '#3b82f6', width: 1 } },
            hovertemplate: '%{y}<extra></extra>',
        };
        const layout = {
            ...PLOTLY_BASE_LAYOUT,
            barmode: 'group', bargap: 0.25,
            xaxis: { ...PLOTLY_BASE_LAYOUT.xaxis, tickfont: { size: 8, color: '#64748b' } },
        };
        Plotly.newPlot('chart-bars', [traceA, traceB], layout, PLOTLY_CONFIG);
    }

  // ── ÚLTIMOS RESULTADOS lado a lado ──
    function renderLastResults(h2hMatches) {
        const box = document.getElementById('h2h-matches');
        if (!box) return;
        
        box.innerHTML = ''; 
    
        if (!h2hMatches || h2hMatches.length === 0) {
            box.innerHTML = `<div style="text-align:center; padding:20px; color:#64748b; font-size:10px; text-transform:uppercase;">Sin datos previos</div>`;
            return;
        }
        
        // El badge de WIN con el estilo neón que te gusta
        const winBadge = `<span style="font-size:8px; font-weight:900; color:#22c55e; border:1px solid #22c55e33; padding:2px 5px; border-radius:3px; background:rgba(34,197,94,0.15); margin: 0 8px; box-shadow: 0 0 10px rgba(34,197,94,0.1);">WIN</span>`;

        h2hMatches.forEach((m) => {
            const row = document.createElement('div');
            // Usamos las 5 columnas que definimos en el HTML
            row.style.display = "grid";
            row.style.gridTemplateColumns = "120px 1fr auto 1fr 120px"; 
            row.style.alignItems = "center";
            row.style.padding = "10px 16px";
            row.style.marginBottom = "6px";
            row.style.borderRadius = "12px";
            row.style.backgroundColor = "rgba(30, 41, 59, 0.4)";
            row.style.border = "1px solid rgba(51, 65, 85, 0.3)";
            
            // Color del marcador según resultado
            let scoreColor = "#94a3b8"; 
            if (m.result === "home") scoreColor = "#22c55e"; 
            if (m.result === "away") scoreColor = "#3b82f6"; 

            row.innerHTML = `
                <span style="font-size:10px; color:#64748b; font-family:monospace; font-weight:bold;">
                    ${m.date || '-'}
                </span>

                <div style="text-align:right; display:flex; align-items:center; justify-content:flex-end;">
                    ${m.result === 'home' ? winBadge : ''}
                    <span style="font-size:11px; font-weight:800; color:#cbd5e1; white-space: nowrap; overflow:hidden; text-overflow:ellipsis;">
                        ${m.home || '-'}
                    </span>
                </div>

                <div style="background:#020617; border:1px solid #334155; padding:3px 12px; border-radius:6px; min-width:75px; text-align:center; margin: 0 15px; box-shadow: inset 0 0 10px rgba(0,0,0,0.5);">
                    <span style="font-family:monospace; font-weight:900; font-size:14px; color:${scoreColor}; letter-spacing:1px;">
                        ${m.score || '-'}
                    </span>
                </div>

                <div style="text-align:left; display:flex; align-items:center; justify-content:flex-start;">
                    <span style="font-size:11px; font-weight:800; color:#cbd5e1; white-space: nowrap; overflow:hidden; text-overflow:ellipsis;">
                        ${m.away || '-'}
                    </span>
                    ${m.result === 'away' ? winBadge : ''}
                </div>

                <div style="text-align:center; font-size:9px; color:#475569; font-family:monospace; font-weight:bold; letter-spacing:1px;">
                    ${m.result === 'draw' ? '<span style="color:#f59e0b; opacity:0.8;">DRAW</span>' : ''}
                </div>
            `;
            box.appendChild(row);
        });
    };


   // ── COMPARACIÓN AJAX ──
   document.getElementById('btn-compare').addEventListener('click', function () {
    const lId = new URLSearchParams(window.location.search).get('league');
    const tA  = document.getElementById('select-local').value;
    const tB  = document.getElementById('select-visitor').value;

    if (!tA || !tB || !lId) {
        alert("Selecciona equipos");
        return;
    }

    const b = this;
    b.innerHTML = "PROCESANDO...";
    b.disabled = true;

    fetch(`/tracker/compare/${lId}/${tA}/${tB}/`)
    .then(r => r.json())
    .then(res => {
        if (res.status !== "success") return;
        
        const d = res.data;
        const view = document.getElementById('results-container');
        if (!view) return;

        // Mostrar todo el bloque de golpe
        view.classList.remove('hidden');
        view.style.display = "block"; 
        view.style.opacity = "1";

        // Datos básicos
        document.getElementById('main-prob').innerText = d.team_a_prob + "%";
        document.getElementById('label-prob-detail').innerText = `${d.team_a_prob}% VS ${d.team_b_prob}%`;
        document.getElementById('bar-prob-a').style.width = d.team_a_prob + "%";
        document.getElementById('bar-prob-b').style.width = d.team_b_prob + "%";

        // Limpiar y rellenar métricas
        const met = document.getElementById('dynamic-metrics');
        met.innerHTML = '';
        d.comparison_table.forEach(i => {
            const row = document.createElement('div');
            row.className = "grid grid-cols-3 gap-2 px-3 py-2 border-b border-slate-800/30";
            row.innerHTML = `<span class="text-green-500 font-black">${i.val_a}</span><span class="text-slate-500 text-center text-[10px] uppercase">${i.metrica}</span><span class="text-blue-500 font-black text-right">${i.val_b}</span>`;
            met.appendChild(row);
        });

        // Gráficos
        const nA = document.getElementById('display-local').innerText;
        const nB = document.getElementById('display-visitor').innerText;
        renderFormChart(d.form_a, d.form_b, nA, nB);
        renderBarChart(d.bar_metrics, nA, nB);

        // TABLA H2H
        if (d.h2h_matches) {
            renderLastResults(d.h2h_matches);
        }

        b.innerHTML = "Iniciar<br>Comparación";
        b.disabled = false;
    })
    .catch(e => {
        console.error(e);
        b.innerHTML = "ERROR";
        b.disabled = false;
        });
    });
});