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
TOKEN_LIST = ["6728e2d7b5c06562344b779385eeed84", "096e2a18cca2f5be6feaa985b556f679"]
token_pool = APITokenPool(TOKEN_LIST)
    

def fetch_competitions():
    """
    Obtiene competiciones de football-data.org
    """
    url = "https://api.football-data.org/v4/competitions/"
    headers = {"X-Auth-Token": "0ba4247e00a64c0cab971f5c657d831f"}
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        # Extrae las competiciones
        if 'competitions' in data:
            return data['competitions']
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []