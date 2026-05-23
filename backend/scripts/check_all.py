import importlib.util
import json
from pathlib import Path
import requests

# Load Django settings for host info
settings_path = Path('e:/HealthDesk/backend/healthdesk/settings.py')
spec = importlib.util.spec_from_file_location('settings', str(settings_path))
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)

BASE_URL = 'http://127.0.0.1:8000'

def login(email, password):
    url = f"{BASE_URL}/api/auth/login/"
    resp = requests.post(url, json={'email': email, 'password': password})
    print(f"Login attempt for {email}: status {resp.status_code}")
    try:
        data = resp.json()
        print(json.dumps(data, indent=2))
        return data.get('access')
    except Exception as e:
        print('Failed to parse JSON:', e)
        return None

def get_profile(token):
    url = f"{BASE_URL}/api/auth/profile/"
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(url, headers=headers)
    print('Profile request status:', resp.status_code)
    try:
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print('Non‑JSON response')

if __name__ == '__main__':
    # Admin credentials
    admin_token = login('admin@gmail.com', 'admin12345')
    if admin_token:
        get_profile(admin_token)
    # Regular user credentials (sample created by DB script)
    user_token = login('test_user@example.com', 'TestPass123!')
    if user_token:
        get_profile(user_token)
