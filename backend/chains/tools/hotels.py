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
            return json.dumps({"error": "Klucz 'city' jest wymagany w JSON na wejściu."})
    except json.JSONDecodeError:
        return json.dumps({"error": "Niepoprawny format JSON na wejściu. Oczekiwano np. '{\"city\": \"Paris\"}'."})

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return json.dumps({"error": "Klucz GOOGLE_API_KEY nie jest ustawiony w pliku .env."})

    # Adres URL do Google Places API - Text Search
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    # Parametry zapytania
    params = {
        "query": f"hotele w {city}",
        "key": api_key,
        "language": "pl" # Możesz zmienić na 'en' jeśli wolisz wyniki po angielsku
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Sprawdza czy nie ma błędów HTTP (np. 4xx, 5xx)
        results_data = response.json()

        # Sprawdzanie statusu odpowiedzi z API Google
        if results_data["status"] != "OK":
            if results_data["status"] == "ZERO_RESULTS":
                 return json.dumps({"message": f"Nie znaleziono hoteli w mieście: {city}."})
            return json.dumps({"error": f"Błąd API Google: {results_data.get('status')}", "details": results_data.get('error_message', '')})

        # Przetwarzanie odpowiedzi, aby była czytelniejsza dla LLM
        simplified_results = []
        # Bierzemy maksymalnie 5 pierwszych wyników
        for place in results_data.get("results", [])[:5]:
            simplified_results.append({
                "name": place.get("name"),
                "address": place.get("formatted_address"),
                "rating": place.get("rating", "Brak oceny"),
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
    description="Użyj tego narzędzia do wyszukiwania hoteli w określonym mieście. Wejście musi być stringiem JSON z kluczem 'city' (np. {'city': 'Paryż'}). Zwraca listę JSON z propozycjami hoteli, zawierającą ich nazwę, adres i ocenę.",
    func=Google_Hotels,
)