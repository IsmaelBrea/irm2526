document.addEventListener('DOMContentLoaded', function() {
    // Toggle Scorers
    const toggleScorersBtn = document.getElementById('toggle-scorers');
    if (toggleScorersBtn) {
        const scorerRows = document.querySelectorAll('.scorer-row');
        let scorersExpanded = false;
        toggleScorersBtn.addEventListener('click', function() {
            scorersExpanded = !scorersExpanded;
            scorerRows.forEach(row => {
                if (row.getAttribute('data-hidden') === 'true') {
                    row.style.display = scorersExpanded ? 'table-row' : 'none';
                }
            });
            toggleScorersBtn.textContent = scorersExpanded ? 'Ver menos' : 'Ver más';
        });
    }

    // Toggle Standings
    const toggleBtn = document.getElementById('toggle-standings');
    if (toggleBtn) {
        const rows = document.querySelectorAll('.standing-row');
        let isExpanded = false;
        toggleBtn.addEventListener('click', function() {
            isExpanded = !isExpanded;
            rows.forEach(row => {
                if (row.getAttribute('data-hidden') === 'true') {
                    row.style.display = isExpanded ? 'table-row' : 'none';
                }
            });
            toggleBtn.textContent = isExpanded ? 'Ver menos' : 'Ver más';
        });
    }
});