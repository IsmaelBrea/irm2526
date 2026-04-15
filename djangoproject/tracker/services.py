import requests
import threading

class APITokenPool:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.lock = threading.Lock()

    def get_token(self):
        with self.lock:
            token = self.tokens[self.index]
            self.index = (self.index + 1) % len(self.tokens)
            return token

# API Keys
TOKEN_LIST = ["6728e2d7b5c06562344b779385eeed84, 096e2a18cca2f5be6feaa985b556f679"]
token_pool = APITokenPool(TOKEN_LIST)

def fetch_team_stats(team_id, league=39, season=2023):
    """
    F13: Obtención de datos desde API-Sports (Directa).
    """

    url = "https://v3.football.api-sports.io/teams/statistics"
    
    headers = {
        "x-apisports-key": token_pool.get_token() # Cabecera correcta para esta URL
    }
    
    params = {"league": league, "season": season, "team": team_id}

    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"DEBUG: Probando conexión directa. Status: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error en la conexión directa: {e}")
        return None