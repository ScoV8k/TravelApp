import requests
import json
import os
from dotenv import load_dotenv
from langchain.tools import Tool

# Ładujemy zmienne środowiskowe z pliku .env
load_dotenv()

def Google_Hotels(input_data: str) -> str:
    try:
        data = json.loads(input_data)
        city = data.get("city")
        if not city:
            return json.dumps({"error": "City is needed"})
    except json.JSONDecodeError:
        return json.dumps({"error": "Bad JSON format. Good example: '{\"city\": \"Paris\"}'."})

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return json.dumps({"error": "Klucz GOOGLE_API_KEY nie jest ustawiony w pliku .env."})

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    params = {
        "query": f"hotels in {city}",
        "key": api_key,
        "language": "en"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results_data = response.json()

        if results_data["status"] != "OK":
            if results_data["status"] == "ZERO_RESULTS":
                 return json.dumps({"message": f"Nie znaleziono hoteli w mieście: {city}."})
            return json.dumps({"error": f"Błąd API Google: {results_data.get('status')}", "details": results_data.get('error_message', '')})

        # Przetwarzanie odpowiedzi, aby była czytelniejsza dla LLM
        simplified_results = []
        # Bierzemy maksymalnie 5 pierwszych wyników
        for place in results_data.get("results", [])[:4]:
            simplified_results.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating", "No rating"),
                "total_ratings": place.get("user_ratings_total", 0)
            })

        if not simplified_results:
            return json.dumps({"message": f"Nie znaleziono hoteli w mieście: {city}."})

        return json.dumps(simplified_results, ensure_ascii=False, indent=2)

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Wystąpił błąd połączenia z API: {e}"})
    except Exception as e:
        return json.dumps({"error": f"Wystąpił nieoczekiwany błąd: {e}"})

# Definicja narzędzia dla LangChain
hotel_searcher_tool = Tool(
    name="hotel_searcher",
    description="Use this tool to search for hotels in a specified city. The input must be a JSON string with the key 'city' (e.g., {'city': 'Paris'}). Returns a JSON list of hotel suggestions, including their name, address, and rating.",
    func=Google_Hotels,
)