
import requests
import json
import os
from dotenv import load_dotenv
from datetime import date, timedelta
from langchain.tools import Tool

load_dotenv()

def search_flights(destination_country: str) -> str:
    print(destination_country)
    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        return json.dumps({"error": "RapidAPI key is not set."})

    # country_to_city_map = {
    #     "France": "paris_fr",
    #     "Italy": "rome_it",
    #     "Spain": "madrid_es",
    #     "Great Britian": "london_gb",
    #     "Germany": "berlin_de"
    # }

    # normalized_country = destination_country.lower()
    # if normalized_country not in country_to_city_map:
    #     return json.dumps({
    #         "error": f"Sorry, I don't have information for the country: {destination_country}. "
    #                  f"Supported countries are: {list(country_to_city_map.keys())}"
    #     })

    # destination_code = country_to_city_map[normalized_country]

    # Ustawienie daty początkowej na za tydzień od dzisiaj
    departure_start_date = (date.today() + timedelta(days=7)).strftime('%Y-%m-%dT00:00:00')
    inbound_start_date = (date.today() + timedelta(days=14)).strftime('%Y-%m-%dT00:00:00')

    url = "https://kiwi-com-cheap-flights.p.rapidapi.com/round-trip"

    # Zostawiamy większość parametrów jak w przykładzie, ale używamy zmiennych dla kluczowych pól
    querystring = {
        "source": "Country:warsaw_pl",
        "destination": f"City:{destination_country.strip()}",
        "locale": "en",
        "adults": "1",
        "children": "0",
        "infants": "0",
        "handbags": "1",
        "holdbags": "0",
        "cabinClass": "ECONOMY",
        "sortBy": "QUALITY",
        "sortOrder": "ASCENDING",
        "limit": "5", # Zwiększamy limit do 5, aby dostać więcej opcji
        "inboundDepartureDateStart": inbound_start_date
    }
    print(querystring)
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "kiwi-com-cheap-flights.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        if not data.get("itineraries"):
            return json.dumps({"message": f"No flights found from Poland to {destination_country}."})

        # Przetwarzanie odpowiedzi, aby była bardziej czytelna dla LLM i użytkownika
        simplified_results = []
        for itinerary in data["itineraries"]:
            try:
                booking_base_url = "https://www.kiwi.com"
                relative_url = itinerary["bookingOptions"]["edges"][0]["node"]["bookingUrl"]
                
                result = {
                    "price_EUR": itinerary["priceEur"]["amount"],
                    "provider": itinerary["provider"]["name"],
                    "booking_link": f"{booking_base_url}{relative_url}",
                    "outbound_flight": {
                        "airline": itinerary["outbound"]["sectorSegments"][0]["segment"]["carrier"]["name"],
                        "departure_from": itinerary["outbound"]["sectorSegments"][0]["segment"]["source"]["station"]["name"],
                        "departure_time": itinerary["outbound"]["sectorSegments"][0]["segment"]["source"]["localTime"],
                        "arrival_to": itinerary["outbound"]["sectorSegments"][0]["segment"]["destination"]["station"]["name"],
                        "arrival_time": itinerary["outbound"]["sectorSegments"][0]["segment"]["destination"]["localTime"],
                    },
                    "inbound_flight": {
                        "airline": itinerary["inbound"]["sectorSegments"][0]["segment"]["carrier"]["name"],
                        "departure_from": itinerary["inbound"]["sectorSegments"][0]["segment"]["source"]["station"]["name"],
                        "departure_time": itinerary["inbound"]["sectorSegments"][0]["segment"]["source"]["localTime"],
                        "arrival_to": itinerary["inbound"]["sectorSegments"][0]["segment"]["destination"]["station"]["name"],
                        "arrival_time": itinerary["inbound"]["sectorSegments"][0]["segment"]["destination"]["localTime"],
                    }
                }
                simplified_results.append(result)
            except (KeyError, IndexError):
                continue
        
        if not simplified_results:
             return json.dumps({"message": f"Could not process flight data for {destination_country}."})

        return json.dumps(simplified_results, ensure_ascii=False, indent=2)

    except requests.exceptions.HTTPError as http_err:
        return json.dumps({"error": f"An HTTP error occurred while searching for flights: {http_err}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred while searching for flights: {e}"})



flight_searcher_tool = Tool(
    name="flight_searcher",
    description="Use this tool to search for round-trip flights from Poland to a specified destination country. The input must like this for City: dubrovnik_hr,warsaw_pl or just code for Country:DE,FR,PL of the destination country in English. It returns a JSON list of available flight options including price, airline, and times.",
    func=search_flights
)
