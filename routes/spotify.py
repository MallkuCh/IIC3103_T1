import os
from dotenv import load_dotenv
from fastapi import APIRouter
import requests
import base64
from .storage import saved_tokens


load_dotenv()
router = APIRouter(tags=["Spotify"])

# Varaibles de entorno
TOKEN = os.getenv("TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.getenv("SPOTIFY_REDIRECT")
URL = f"https://api.telegram.org/bot{TOKEN}"

@router.get("/callback")
async def callback(code: str, state: str):
    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth = base64.b64encode(auth_str.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_REDIRECT,
        },
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )

    token = response.json()
    saved_tokens[state] = {
        "access_token": token["access_token"],
        "refresh_token": token["refresh_token"]
    }
    response = "Autenticacion exitosa!!"

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={
            "chat_id": state,
            "text": "Spotify conectado!!!"
        }
    )

    return response
