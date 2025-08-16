import os
import requests
from dotenv import load_dotenv

load_dotenv(".env")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


def refresh_access_token(refresh_token):
    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post(SPOTIFY_TOKEN_URL, data=payload)
    
    if response.status_code != 200:
        print(f"Error refreshing token: {response.text}")
        return None

    new_tokens = response.json()
    return new_tokens.get("access_token")


def get_user_id(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{SPOTIFY_API_BASE_URL}/me", headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to get user ID: {response.text}")
        
    return response.json().get("id")


def get_tracks_from_playlist(access_token, playlist_id):

    all_track_ids = []
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{SPOTIFY_API_BASE_URL}/playlists/{playlist_id}/tracks"

    while url:
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching playlist tracks: {response.text}")

        data = response.json()
        for item in data.get("items", []):
            if item.get("track") and item["track"].get("id"):
                all_track_ids.append(item["track"]["id"])
        
        url = data.get("next")

    return all_track_ids


def get_suggestions(track_ids):
    suggested_track_ids = []
    headers = {'Accept': 'application/json'}
    
    for i in range(0, len(track_ids), 5):
        chunk = track_ids[i:i+5]
        params = {'seeds': chunk, 'size': 7}
        
        try:
            response = requests.get(
                "https://api.reccobeats.com/v1/track/recommendation",
                headers=headers,
                params=params
            )
            response.raise_for_status()  
            
            data = response.json()
            for track in data.get("content", []):
                href = track.get("href")
                if href:
                    track_id = href.rstrip('/').split('/')[-1]
                    # Ensure no duplicates are added
                    if track_id not in suggested_track_ids and track_id not in track_ids:
                        suggested_track_ids.append(track_id)
        except requests.exceptions.RequestException as e:
            print(f"Error getting suggestions: {e}")
            
    return suggested_track_ids


def create_playlist(access_token, playlist_name, track_ids_to_add):
    user_id = get_user_id(access_token)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    playlist_creation_data = {
        "name": playlist_name,
        "description": "Created with the awesome playlist generator",
        "public": True
    }
    response = requests.post(
        f"{SPOTIFY_API_BASE_URL}/users/{user_id}/playlists",
        headers=headers,
        json=playlist_creation_data
    )
    
    if response.status_code != 201:
        raise Exception(f"Failed to create playlist: {response.text}")

    playlist_data = response.json()
    new_playlist_id = playlist_data["id"]

    for i in range(0, len(track_ids_to_add), 100):
        chunk = track_ids_to_add[i:i+100]
        track_uris = [f"spotify:track:{track_id}" for track_id in chunk]
        
        add_tracks_data = {"uris": track_uris}
        add_response = requests.post(
            f"{SPOTIFY_API_BASE_URL}/playlists/{new_playlist_id}/tracks",
            headers=headers,
            json=add_tracks_data
        )
        if add_response.status_code != 201:
            print(f"Warning: Failed to add a batch of songs: {add_response.text}")

    return playlist_data.get("external_urls", {}).get("spotify")