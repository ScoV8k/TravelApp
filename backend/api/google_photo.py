from fastapi import APIRouter, Response
import os
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

router = APIRouter(prefix="/plans", tags=["Plans"])

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@lru_cache(maxsize=1000)
def get_google_photo_bytes(photoreference: str) -> bytes:
    import requests
    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photoreference}&key={GOOGLE_MAPS_API_KEY}"
    r = requests.get(url, allow_redirects=True)
    if r.status_code != 200:
        return b""
    return r.content

@router.get("/proxy/photo")
def proxy_photo(photoreference: str):
    photo_bytes = get_google_photo_bytes(photoreference)
    return Response(content=photo_bytes, media_type="image/jpeg")
