document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const teamId = this.dataset.teamId;
            const teamName = this.dataset.teamName;
            const teamCrest = this.dataset.teamCrest;
            const leagueId = this.dataset.leagueId;
            const svg = this.querySelector('svg');
            
            fetch('/tracker/toggle-favorite/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `team_id=${teamId}&team_name=${teamName}&team_crest=${teamCrest}&league_id=${leagueId}`
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    if(data.is_favorite) {
                        svg.classList.remove('fill-none', 'stroke-slate-400', 'hover:stroke-green-500');
                        svg.classList.add('fill-green-500', 'stroke-green-500');
                    } else {
                        svg.classList.remove('fill-green-500', 'stroke-green-500');
                        svg.classList.add('fill-none', 'stroke-slate-400', 'hover:stroke-green-500');
                    }
                }
            })
            .catch(err => console.error('Error:', err));
        });
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}