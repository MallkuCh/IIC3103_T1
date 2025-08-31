import os
from dotenv import load_dotenv
from fastapi import FastAPI
from routes import spotify, telegram

load_dotenv()

saved_tokens = {}

app = FastAPI()
# Varaibles de entorno
TOKEN = os.getenv("TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT = os.getenv("SPOTIFY_REDIRECT")
URL = f"https://api.telegram.org/bot{TOKEN}"

app = FastAPI()
app.include_router(spotify.router)
app.include_router(telegram.router)
