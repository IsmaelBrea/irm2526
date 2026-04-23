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
    xaxis: {
        gridcolor:     '#1e293b',
        linecolor:     '#334155',
        tickfont:      { size: 9, color: '#64748b' },
        zeroline:      false,
    },
    yaxis: {
        gridcolor:     '#1e293b',
        linecolor:     '#334155',
        tickfont:      { size: 9, color: '#64748b' },
        zeroline:      false,
    },
};

const PLOTLY_CONFIG = { displayModeBar: false, responsive: true };

document.addEventListener('DOMContentLoaded', function () {

    // ── RESET AL CARGAR ──
    const resetSelectors = () => {
        ['search-local', 'search-visitor'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        ['select-local', 'select-visitor'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.value = '';
        });
        ['display-local', 'display-visitor'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerText = '[ SIN SELECCIÓN ]';
                el.className = "h-14 border border-dashed border-slate-800 rounded-[1.2rem] flex items-center justify-center text-slate-500 text-[10px] uppercase font-mono px-6 text-center transition-all duration-300";
            }
        });
        const container = document.getElementById('results-container');
        if (container) container.classList.add('hidden');
    };

    resetSelectors();

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
                const id   = this.dataset.id;
                const name = this.dataset.name;

                const otherSearch = hiddenInputId === 'select-local' ? 'search-visitor' : 'search-local';
                const otherName   = document.getElementById(otherSearch).value;

                if (name === otherName) {
                    alert("ERROR IRM: No puedes seleccionar el mismo equipo.");
                    return;
                }

                hidden.value      = id;
                searchInp.value   = name;
                display.innerText = name;
                display.className = "h-14 border border-dashed border-green-500/40 bg-green-500/5 rounded-[1.2rem] flex items-center justify-center text-green-500 text-xs font-black uppercase font-mono px-6 text-center shadow-inner";
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
        const input   = document.getElementById(inputId);
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
        [lDisp.innerText, vDisp.innerText] = [vDisp.innerText, lDisp.innerText];
        [lDisp.className, vDisp.className] = [vDisp.className, lDisp.className];
    });

    // ── GRÁFICO DE LÍNEAS: forma últimos 5 partidos ──
    function renderFormChart(formA, formB, nameA, nameB) {
        const jornadas = formA.map(d => d.jornada);

        const traceA = {
            x:    jornadas,
            y:    formA.map(d => d.pts),
            name: nameA,
            mode: 'lines+markers',
            line:   { color: '#22c55e', width: 2.5, shape: 'spline' },
            marker: { color: '#22c55e', size: 7, symbol: 'circle' },
            text:   formA.map(d => `vs ${d.rival}<br>${d.score}`),
            hovertemplate: '<b>%{text}</b><br>Puntos: %{y}<extra></extra>',
        };

        const traceB = {
            x:    formB.map(d => d.jornada),
            y:    formB.map(d => d.pts),
            name: nameB,
            mode: 'lines+markers',
            line:   { color: '#3b82f6', width: 2.5, shape: 'spline' },
            marker: { color: '#3b82f6', size: 7, symbol: 'circle' },
            text:   formB.map(d => `vs ${d.rival}<br>${d.score}`),
            hovertemplate: '<b>%{text}</b><br>Puntos: %{y}<extra></extra>',
        };

        const layout = {
            ...PLOTLY_BASE_LAYOUT,
            yaxis: {
                ...PLOTLY_BASE_LAYOUT.yaxis,
                tickvals: [0, 1, 3],
                ticktext: ['D (0)', 'Empate (1)', 'Victoria (3)'],
                range: [-0.3, 3.5],
            },
        };

        Plotly.newPlot('chart-form', [traceA, traceB], layout, PLOTLY_CONFIG);
    }

    // ── GRÁFICO DE BARRAS: métricas comparativas ──
    function renderBarChart(barMetrics, nameA, nameB) {
        const labels = barMetrics.map(d => d.metrica);

        const traceA = {
            x:           labels,
            y:           barMetrics.map(d => d.val_a),
            name:        nameA,
            type:        'bar',
            marker:      { color: 'rgba(34,197,94,0.75)', line: { color: '#22c55e', width: 1 } },
            hovertemplate: '%{y}<extra></extra>',
        };

        const traceB = {
            x:           labels,
            y:           barMetrics.map(d => d.val_b),
            name:        nameB,
            type:        'bar',
            marker:      { color: 'rgba(59,130,246,0.75)', line: { color: '#3b82f6', width: 1 } },
            hovertemplate: '%{y}<extra></extra>',
        };

        const layout = {
            ...PLOTLY_BASE_LAYOUT,
            barmode: 'group',
            bargap:  0.25,
            xaxis: {
                ...PLOTLY_BASE_LAYOUT.xaxis,
                tickfont: { size: 8, color: '#64748b' },
            },
        };

        Plotly.newPlot('chart-bars', [traceA, traceB], layout, PLOTLY_CONFIG);
    }

    // ── COMPARACIÓN AJAX ──
    document.getElementById('btn-compare').addEventListener('click', function () {
        const leagueId = new URLSearchParams(window.location.search).get('league');
        const teamA    = document.getElementById('select-local').value;
        const teamB    = document.getElementById('select-visitor').value;

        if (!teamA || !teamB || !leagueId) {
            alert("Selecciona ambos equipos para procesar los datos");
            return;
        }

        const btn     = this;
        btn.innerHTML = `<span style="font-size:10px;letter-spacing:0.1em;">PROCESANDO...</span>`;
        btn.disabled  = true;

        fetch(`/tracker/compare/${leagueId}/${teamA}/${teamB}/`)
            .then(res => res.json())
            .then(response => {
                if (response.status !== "success") throw new Error(response.message || "Error desconocido");

                const results          = response.data;
                const container        = document.getElementById('results-container');
                const metricsContainer = document.getElementById('dynamic-metrics');
                if (!container || !metricsContainer) return;

                metricsContainer.innerHTML = '';

                // Mostrar contenedor
                container.classList.remove('hidden');
                container.style.opacity    = '0';
                container.style.transform  = 'translateY(8px)';
                container.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                setTimeout(() => {
                    container.style.opacity   = '1';
                    container.style.transform = 'translateY(0)';
                }, 30);

                // Probabilidades
                document.getElementById('main-prob').innerText         = results.team_a_prob + "%";
                document.getElementById('label-prob-detail').innerText = `${results.team_a_prob}% VS ${results.team_b_prob}%`;
                document.getElementById('bar-prob-a').style.width      = results.team_a_prob + "%";
                document.getElementById('bar-prob-b').style.width      = results.team_b_prob + "%";

                const nameA = document.getElementById('display-local').innerText;
                const nameB = document.getElementById('display-visitor').innerText;

                document.getElementById('name-a').innerText = nameA;
                document.getElementById('name-b').innerText = nameB;

                // Filas de métricas
                results.comparison_table.forEach((item, index) => {
                    const row = document.createElement('div');
                    row.className = "grid grid-cols-3 gap-2 px-3 py-2 rounded-lg hover:bg-slate-800/60 transition-colors duration-200";
                    row.style.cssText = `opacity:0; transform:translateX(15px); animation:fadeInRight 0.35s ease forwards ${index * 0.07}s;`;
                    row.innerHTML = `
                        <span style="font-size:14px;font-weight:800;color:#22c55e;font-family:monospace;">${item.val_a}</span>
                        <span style="font-size:11px;font-weight:700;color:#64748b;text-align:center;text-transform:uppercase;letter-spacing:0.04em;">${item.metrica}</span>
                        <span style="font-size:14px;font-weight:800;color:#3b82f6;font-family:monospace;text-align:right;">${item.val_b}</span>
                    `;
                    metricsContainer.appendChild(row);
                });

                // Gráficos Plotly
                if (results.form_a && results.form_b) {
                    renderFormChart(results.form_a, results.form_b, nameA, nameB);
                }
                if (results.bar_metrics) {
                    renderBarChart(results.bar_metrics, nameA, nameB);
                }

                btn.innerHTML = "Iniciar<br>Comparación";
                btn.disabled  = false;
            })
            .catch(err => {
                console.error("IRM Engine error:", err);
                btn.innerHTML = "INICIAR COMPARACIÓN";
                btn.disabled  = false;
            });
    });
});