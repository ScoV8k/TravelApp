import os
from dotenv import load_dotenv
import googlemaps

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

async def enrich_place_with_googlemaps_client(place_name: str, city: str):
    if not gmaps:
        raise ValueError("Google Maps client is not initialized")

    find_result = gmaps.find_place(
        input= place_name + ", " + city,
        input_type="textquery",
        fields=[
            "place_id", 
            "name", 
            "formatted_address", 
            "geometry",
            "photos" 
        ]
    )
    
    candidates = find_result.get("candidates", [])
    if not candidates:
        print(f"Nie znaleziono kandydatów dla: {place_name}")
        return None
    result = candidates[0]

    place_id = candidates[0]["place_id"]
    # photo_url = None
    photos = result.get("photos")
    if photos:
        photo_reference = photos[0].get("photo_reference")
        # if photo_reference:
        #     photo_url = get_place_photo_url(photo_reference)

    return {
        "place_id": place_id,
        "name": result.get("name", place_name),
        "formatted_address": result.get("formatted_address", ""),
        "lat": result.get("geometry", {}).get("location", {}).get("lat"),
        "lng": result.get("geometry", {}).get("location", {}).get("lng"),
        "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
        # "photo_url": photo_url
        "photo_reference": photo_reference
    }



async def enrich_plan_with_locations(plan_data: dict) -> dict:
    for day in plan_data.get("daily_plan", []):
        city = day.get("city")
        for activity in day.get("activities", []):
            place_name = activity.get("location_name")
            if place_name and ("lat" not in activity or "lng" not in activity):
                enriched = await enrich_place_with_googlemaps_client(place_name, city)
                if enriched:
                    activity.update({
                    "place_id": enriched["place_id"],
                    "lat": enriched["lat"],
                    "lng": enriched["lng"],
                    "formatted_address": enriched["formatted_address"],
                    # "google_maps_url": enriched["google_maps_url"],
                    "maps_url": enriched["google_maps_url"],
                    # "photo_url": enriched.get("photo_url")
                    "photo_reference": enriched["photo_reference"]
                })


    return plan_data


def get_place_photo_url(photo_reference: str, maxwidth: int = 800):
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxwidth}&photoreference={photo_reference}&key={os.getenv('GOOGLE_MAPS_API_KEY')}"
