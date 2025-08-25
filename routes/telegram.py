import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi import APIRouter
import requests
from urllib.parse import urlencode
from .spotify import current_song, resume_song, pause_song, next_song, previous_song, search_songs, save_track_to_spotify, help_command
from .storage import saved_idchats, saved_tokens

load_dotenv()
router = APIRouter(tags=["Telegram"])

# Varaibles de entorno
TOKEN = os.getenv("TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.getenv("SPOTIFY_REDIRECT")
URL = f"https://api.telegram.org/bot{TOKEN}"

@router.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print(data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        texto = data["message"].get("text", "")

        if texto.startswith("/"):
            if texto == "/help":
                respuesta = help_command()
            elif texto == "/install":
                scopes = "user-read-currently-playing user-read-playback-state user-modify-playback-state user-library-modify"
                params = {
                    "client_id": SPOTIFY_CLIENT_ID,
                    "response_type": "code",
                    "redirect_uri": SPOTIFY_REDIRECT,
                    "state": str(chat_id),
                    "scope": scopes
                }
                auth_url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
                respuesta = f"Inicia Sesion de Spotify aquí:\n{auth_url}"
                requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": respuesta})
            elif texto == "/current":
                respuesta = current_song(chat_id)
            elif texto == "/play":
                respuesta = await resume_song(chat_id)
            elif texto == "/pause":
                respuesta = await pause_song(chat_id)
            elif texto == "/next":
                respuesta = next_song(chat_id)
            elif texto == "/previous":
                respuesta = previous_song(chat_id)
            elif texto.startswith("/search"):
                query = texto.replace("/search", "").strip()
                if chat_id in saved_tokens:
                    if query == "" or query == " ":
                        respuesta = "Debes escribir algo, por ejemplo /search pop"
                    else:
                        respuesta, tracks_ids = search_songs(chat_id, query)
                        for mensaje in respuesta:
                            resp_telegram = requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"})
                            response = resp_telegram.json()
                            message_id = response["result"]["message_id"]
                            try:
                                saved_idchats[message_id] = tracks_ids[mensaje]
                            except:
                                print("me¿nsaje no encontrado")
                        print(saved_idchats)
                        return 0
                else:
                    respuesta = "Por favor primero inicia sesion en Spotify!"
            else:
                respuesta = "Comando no reconocido."
            requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": respuesta, "parse_mode": "Markdown"})
        else:
            respuesta = f"Recibí tu mensaje: {texto}"
            requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": respuesta, "parse_mode": "Markdown"})
    elif "message_reaction" in data:
        print("reaccion!!!")
        chat_id = data["message_reaction"]["chat"]["id"]
        reaction_event = data["message_reaction"]
        message_id = reaction_event["message_id"]
        track_id = saved_idchats.get(message_id)
        if track_id:
            respuesta = save_track_to_spotify(chat_id, track_id)
            requests.post(f"{URL}/sendMessage", json={"chat_id": chat_id, "text": respuesta, "parse_mode": "Markdown"})

    return {"ok": True}