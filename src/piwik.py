import requests
from .payloads import SESSIONS, EVENTS, ANALYTICS


def get_token(auth_url, client_id, client_secret):
    """Get bearer token"""
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(auth_url, json=data)
    response.raise_for_status()
    return response.json()["access_token"]


def extract_endpoint(base_url, endpoint, token, website_id, date_from, date_to):
    """Extract data from Piwik endpoint"""
    url = f"{base_url}{endpoint}/"

    # Basic payload for all endpoints
    payload = {
        "website_id": website_id,
        "date_from": date_from,
        "date_to": date_to,
        "filters": {"operator": "and", "conditions": []},
        "offset": 0,
        "limit": 10000,
        "format": "json",
    }

    # Add endpoint-specific columns
    if endpoint == "sessions":
        payload["columns"] = SESSIONS
    elif endpoint == "events":
        payload["columns"] = EVENTS

    else:  # analytics
        payload["columns"] = ANALYTICS

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
