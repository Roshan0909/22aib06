import requests
from datetime import datetime

AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJuYWdhcm9zaGFuXzIyYWliMDZAa2draXRlLmFjLmluIiwiZXhwIjoxNzU2NzA0NjE0LCJpYXQiOjE3NTY3MDM3MTQsImlzcyI6IkFmZm9yZCBNZWRpY2FsIFRlY2hub2xvZ2llcyBQcml2YXRlIExpbWl0ZWQiLCJqdGkiOiJkNjg5YzQzMC05NmI5LTQ2MzMtYmEzMy1lZTQxMmQyMDQ4ZGQiLCJsb2NhbGUiOiJlbi1JTiIsIm5hbWUiOiJuYWdhcm9zaGFuIG5zIiwic3ViIjoiNzI4MzZiYzUtMjA3NS00MDEyLTg5ZjUtN2ViNjZkNGFkZjNiIn0sImVtYWlsIjoibmFnYXJvc2hhbl8yMmFpYjA2QGtna2l0ZS5hYy5pbiIsIm5hbWUiOiJuYWdhcm9zaGFuIG5zIiwicm9sbE5vIjoiMjJhaWIwNiIsImFjY2Vzc0NvZGUiOiJkcVh1d1oiLCJjbGllbnRJRCI6IjcyODM2YmM1LTIwNzUtNDAxMi04OWY1LTdlYjY2ZDRhZGYzYiIsImNsaWVudFNlY3JldCI6IndRYXdtdE5ITldEU1pBTnIifQ.jKO6vDr_KZ3MLpBJUvAcPOjP-ioyQiOdhdvv0TJBizs"
LOG_URL = "http://20.244.56.144/evaluation-service/logs"
CLIENT_ID = "72836bc5-2075-4012-89f5-7eb66d4adf3b"
CLIENT_SECRET = "wQawmtNHNWDSZANr"

def Log(stack, level, package, message):
    if stack not in ["frontend", "backend", "database"]:
        return False
    if level not in ["debug", "info", "warn", "error"]:
        return False
    if not package or not message:
        return False
    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }
    try:
        response = requests.post(LOG_URL, headers=headers, json=payload, timeout=5)
        if response.status_code == 200:
            print(f"[{datetime.now().isoformat()}] LOG_SUCCESS: {message}")
            return True
        else:
            print(f"[{datetime.now().isoformat()}] LOG_ERROR: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[{datetime.now().isoformat()}] LOG_ERROR: {str(e)}")
        return False
