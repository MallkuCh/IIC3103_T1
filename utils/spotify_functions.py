import os
import requests
import base64
from routes.storage import saved_tokens



def help_command():
    text = f"""Comandos disponibles:\n
    /install - Iniciar Sesion en Spotify\n
    /current - Mostrar cancion actual\n
    /help - Mostrar esta ayuda\n
    /search - Buscar canciones en Spotify\n
    /play - Reproducir canción\n
    /pause - Pausar canción\n
    /next - Siguiente canción\n
    /previous - Canción anterior\n"""
    return text


def current_song(chat_id: int):
    chat_id = str(chat_id)
    if chat_id in saved_tokens:
        access_token = saved_tokens[chat_id]["access_token"]
        response = requests.get(
            "https://api.spotify.com/v1/me/player/currently-playing",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if response.status_code == 204:
            text = "No se esta reproduciendo ninguna cancion!"
        elif response.status_code != 200:
            text = f"Error: {response.json()}"
        elif response.status_code == 401:
            text = "Sesion expirada, inicie sesion nuevamente con /install"
        else:
            data = response.json()
            track = data["item"]["name"]
            artist = ", ".join([a["name"] for a in data["item"]["artists"]])
            url = data["item"]["external_urls"]["spotify"]
            text = f"Estás escuchando: *{track}* de *{artist}*"

        return text
    else:
        return "Por favor primero inicia sesion en Spotify!"
    
async def pause_song(chat_id: int):
    chat_id = str(chat_id)
    if chat_id in saved_tokens:
        access_token = saved_tokens[chat_id]["access_token"]

        response = requests.put(
            "https://api.spotify.com/v1/me/player/pause",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code == 204 or response.status_code == 200 or response.status_code == 403:
            text = "Cancion pausada"
        else:
            text = f"Error"
        return text
    else:
        return "Por favor primero inicia sesion en Spotify!"
    
async def resume_song(chat_id: int):
    chat_id = str(chat_id)
    if chat_id in saved_tokens:
        access_token = saved_tokens[chat_id]["access_token"]
        active = requests.get(
            "https://api.spotify.com/v1/me/player", 
            headers={"Authorization": f"Bearer {access_token}"}
        )
        if active.status_code == 200:
            active = active.json()
        elif active.status_code == 204:
            return f"No hay canción reproduciéndose en este momento o no hay dispositivos activos!"
        if active:
            if not active.get("is_playing"):  
                response = requests.put(
                    "https://api.spotify.com/v1/me/player/play",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                if response.status_code == 204 or response.status_code == 200 or response.status_code == 403:
                    text = f"cancion reanudada"
                else:
                    text = f"Error"
            else:
                text = f"La cancion ya se esta reproduciendo"
                return text
        else:
            return {"error": "No active device"}
        return text
    else:
        return "Por favor primero inicia sesion en Spotify!"

def next_song(chat_id: int):
    chat_id = str(chat_id)
    if chat_id in saved_tokens:
        print("")
        access_token = saved_tokens[chat_id]["access_token"]
        url = "https://api.spotify.com/v1/me/player/next"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            text = "Tocando siguiente cancion!!"
        else:
            text = "No se pudo reproducir la siguiente cancion!"
        return text
    else:
        return "Por favor primero inicia sesion en Spotify!"
    
def previous_song(chat_id: int):
    chat_id = str(chat_id)
    if chat_id in saved_tokens:
        access_token = saved_tokens[chat_id]["access_token"]
        url = "https://api.spotify.com/v1/me/player/previous"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            text = "Tocando la cancion anterior!!"
        else:
            text = "No se pudo reproducir la cancion!"
        return text
    else:
        return f"Por favor primero inicia sesion en Spotify!"
    
def search_songs(chat_id, query):
    chat_id = str(chat_id)
    if chat_id in saved_tokens:
        access_token = saved_tokens[chat_id]["access_token"]
        url = "https://api.spotify.com/v1/search"
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {
            "q": query,
            "type": "track",
            "limit": 5
        }
        response = requests.get(url, headers=headers, params=params)
        response = response.json()
        canciones = response["tracks"]["items"]
        if canciones:
            mensaje = ["Resultados:\nPuedes Reaccionar con <3 para agregar a tus favoritos\n\n"]
            dict_tracks = {}
            print(canciones[0])
            for track in canciones:
                nombre = track["name"]
                track_id = track["id"]
                artistas = ", ".join([a["name"] for a in track["artists"]])
                cancion = f"*{nombre}* - **{artistas}**\n\n"
                mensaje.append(cancion)
                dict_tracks[cancion] = track_id
            return mensaje, dict_tracks
    else: 
        return f"Por favor primero inicia sesion en Spotify!", None
    
def save_track_to_spotify(chat_id, track_id):
    chat_id = str(chat_id)
    if chat_id in saved_tokens:
        access_token = saved_tokens[chat_id]["access_token"]
        url = "https://api.spotify.com/v1/me/tracks"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {"ids": [track_id]}

        response = requests.put(url, headers=headers, json=data)

        if response.status_code == 200:
            return f"Cancion agregada a tus favoritos"
        else:
            return f"Error"
    else:
        return f"Por favor primero inicia sesion en Spotify!"