import os
import urllib.parse as urlparse
from flask import *
from dotenv import load_dotenv
from spotify import get_tracks_from_playlist, get_suggestions, create_playlist, refresh_access_token
import requests
from datetime import date


from db import add_playlist, list_playlists, remove_playlist, init_db

load_dotenv(".env")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPE = "playlist-modify-public playlist-modify-private"

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

init_db()

def build_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    return "https://accounts.spotify.com/authorize?" + urlparse.urlencode(params)

def exchange_code_for_token(code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=data)
    response.raise_for_status()
    tokens = response.json()
    return tokens.get("access_token"), tokens.get("refresh_token")

@app.route("/")
def home():
    access_token = session.get("access_token")
    playlist_url = session.pop("playlist_url", None)
    return render_template("home.html", access_token=access_token, playlist_url=playlist_url)

@app.route("/create_playlist", methods=["POST"])
def create_playlist_route():
    access_token = session.get("access_token")
    refresh_token = session.get("refresh_token")

    if not access_token or not refresh_token:
        return redirect(url_for("login"))

    playlist_id = request.form.get("playlist_id", "").strip()
    playlist_name = request.form.get("playlist_name", "").strip()

    if not playlist_id or not playlist_name:
        flash("Erro.", "error")
        return redirect(url_for("home"))

    playlist_id = playlist_id.split("/")[-1].split("?")[0]

    try:
        tracks = get_tracks_from_playlist(access_token, playlist_id)
        suggestions = get_suggestions(tracks)
        playlist_url = create_playlist(access_token, playlist_name, suggestions)

    except Exception as e:
        if "The access token expired" in str(e):
            
            # Get a new token
            new_access_token = refresh_access_token(refresh_token)
            
            if not new_access_token:
                flash("Sessão expirada: ", "error")
                return redirect(url_for("logout"))
            
            session["access_token"] = new_access_token

            try:
                tracks = get_tracks_from_playlist(new_access_token, playlist_id)
                suggestions = get_suggestions(tracks)
                playlist_url = create_playlist(new_access_token, playlist_name, suggestions)
            except Exception as retry_e:
                flash(f"Erro: {retry_e}", "error")
                return redirect(url_for("home"))
        else:
            flash(f"Erro: {e}", "error")
            return redirect(url_for("home"))

    session["playlist_url"] = playlist_url
    if playlist_url:
        add_playlist(name=playlist_name, link=playlist_url, date=date.today(), rating=None)
        flash("Playlist criada!", "success")

    return redirect(url_for("home"))

@app.route("/my_playlists")
def show_playlists():
    try:
        all_playlists = list_playlists()
        return render_template("playlists.html", playlists=all_playlists)
    except Exception as e:
        flash(f"Erro: {e}", "error")
        return redirect(url_for("home"))

@app.route("/playlists/delete/<int:playlist_id>", methods=["POST"])
def delete_playlist(playlist_id):
    """Deletes a playlist from our database."""
    success = remove_playlist(playlist_id)
    if success:
        flash("Playlist removida", "success")
    else:
        flash("Falha.", "error")
    return redirect(url_for("show_playlists"))

@app.route("/login")
def login():
    return redirect(build_auth_url())

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization failed or denied.", 400
    try:
        access_token, refresh_token = exchange_code_for_token(code)
        session["access_token"] = access_token
        session["refresh_token"] = refresh_token
    except Exception as e:
        return f"Token exchange failed: {e}", 500
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888, debug=True)