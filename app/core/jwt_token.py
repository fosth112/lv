import requests
from app.config.settings import UID, PASS, URL

def get_jwt():
    try:
        params = {
            'uid': UID,
            'password': PASS
        }
        response = requests.get(URL, params=params)
        if response.status_code == 200:
            jwt_data = response.json()
            return jwt_data.get("token")
        return None
    except Exception:
        return None
