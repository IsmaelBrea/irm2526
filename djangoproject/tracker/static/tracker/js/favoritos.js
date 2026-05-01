document.querySelectorAll('.remove-favorite').forEach(btn => {
    btn.addEventListener('click', function() {
        const teamId = this.dataset.teamId;
        const teamName = this.dataset.teamName;
        
        fetch('/tracker/toggle-favorite/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `team_id=${teamId}&team_name=${teamName}`
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                location.reload();
            }
        })
        .catch(err => console.error('Error:', err));
    });
});

// Función para obtener CSRF token
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