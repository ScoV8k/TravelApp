import requests
import json
import os
from dotenv import load_dotenv
from datetime import date, timedelta
from langchain.tools import Tool

load_dotenv()

def search_flights(input_data: str) -> str:
    try:
        user_input = json.loads(input_data)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid input format. Expected a valid JSON string."})

    api_key = os.environ.get("RAPIDAPI_KEY")
    if not api_key:
        return json.dumps({"error": "RAPIDAPI_KEY is not set in environment variables."})

    if "destination" not in user_input or "source" not in user_input:
        return json.dumps({"error": "The 'source' and 'destination' parameters are required."})

    defaults = {
        "source_type": "City",
        "destination_type": "City",
        "departure_start_date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
        "departure_end_date": (date.today() + timedelta(days=7)).strftime('%Y-%m-%d'),
        "inbound_start_date": None,
        "inbound_end_date": None,
        "currency": "USD",
        "locale": "en",
        "adults": "1",
        "children": "0",
        "infants": "0",
        "handbags": "1",
        "holdbags": "0",
        "cabinClass": "ECONOMY",
        "sortBy": "PRICE",
        "sortOrder": "ASCENDING",
        "limit": "1",
        "applyMixedClasses": "true",
        "allowReturnFromDifferentCity": "true",
        "allowChangeInboundDestination": "true",
        "enableSelfTransfer": "true"
    }

    params = {**defaults, **user_input}

    is_round_trip = params.get("inbound_start_date") is not None
    api_endpoint = "round-trip" if is_round_trip else "one-way"
    url = f"https://kiwi-com-cheap-flights.p.rapidapi.com/{api_endpoint}"

    querystring = {
        "source": f"{params['source_type']}:{params['source']}",
        "destination": f"{params['destination_type']}:{params['destination']}",
        "outboundDepartmentDateStart": f"{params['departure_start_date']}T00:00:00",
        "outboundDepartmentDateEnd": f"{params['departure_end_date']}T23:59:59",
        "currency": params["currency"],
        "locale": params["locale"],
        "adults": str(params["adults"]),
        "children": str(params["children"]),
        "infants": str(params["infants"]),
        "handbags": str(params["handbags"]),
        "holdbags": str(params["holdbags"]),
        "cabinClass": params["cabinClass"].upper(),
        "sortBy": params["sortBy"].upper(),
        "sortOrder": params["sortOrder"].upper(),
        "limit": str(params["limit"]),
        "applyMixedClasses": str(params["applyMixedClasses"]).lower(),
        "allowReturnFromDifferentCity": str(params["allowReturnFromDifferentCity"]).lower(),
        "allowChangeInboundDestination": str(params["allowChangeInboundDestination"]).lower(),
        "enableSelfTransfer": str(params["enableSelfTransfer"]).lower()
    }

    if is_round_trip:
        querystring["inboundDepartureDateStart"] = f"{params['inbound_start_date']}T00:00:00"
        inbound_end = params.get("inbound_end_date") or params["inbound_start_date"]
        querystring["inboundDepartureDateEnd"] = f"{inbound_end}T23:59:59"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "kiwi-com-cheap-flights.p.rapidapi.com"
    }
    print(querystring)

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()

        if not data.get("itineraries"):
            return json.dumps({"message": f"No flights found from {params['source']} to {params['destination']} for the given criteria."})

        simplified_results = []
        for itinerary in data.get("itineraries", []):
            try:
                result = {
                    "price": f"{itinerary.get('priceEur', {}).get('amount')} {params['currency']}",
                    "provider": itinerary.get("provider", {}).get("name"),
                    "booking_link": f"https://www.kiwi.com{itinerary['bookingOptions']['edges'][0]['node']['bookingUrl']}",
                }
                outbound_segment = itinerary.get("outbound", {}).get("sectorSegments", [{}])[0].get("segment", {})
                result["outbound_flight"] = {
                    "airline": outbound_segment.get("carrier", {}).get("name"),
                    "departure_from": outbound_segment.get("source", {}).get("station", {}).get("name"),
                    "departure_time": outbound_segment.get("source", {}).get("localTime"),
                    "arrival_to": outbound_segment.get("destination", {}).get("station", {}).get("name"),
                    "arrival_time": outbound_segment.get("destination", {}).get("localTime"),
                }
                if is_round_trip and "inbound" in itinerary:
                    inbound_segment = itinerary.get("inbound", {}).get("sectorSegments", [{}])[0].get("segment", {})
                    result["inbound_flight"] = {
                        "airline": inbound_segment.get("carrier", {}).get("name"),
                        "departure_from": inbound_segment.get("source", {}).get("station", {}).get("name"),
                        "departure_time": inbound_segment.get("source", {}).get("localTime"),
                        "arrival_to": inbound_segment.get("destination", {}).get("station", {}).get("name"),
                        "arrival_time": inbound_segment.get("destination", {}).get("localTime"),
                    }
                simplified_results.append(result)
            except (KeyError, IndexError):
                continue
        
        if not simplified_results:
             return json.dumps({"message": f"Could not process flight data for {params['destination']}."})

        return json.dumps(simplified_results, ensure_ascii=False, indent=2)

    except requests.exceptions.HTTPError as http_err:
        return json.dumps({"error": f"An HTTP error occurred while searching for flights: {http_err}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred while searching for flights: {e}"})


flight_searcher_tool = Tool(
    name="flight_searcher",
    description="""Use this tool to search for one-way or round-trip flights.
The input must be a JSON object containing at least 'source' and 'destination'.
Locations must be Kiwi location codes (e.g., 'warsaw_pl', 'krakow_pl', 'london_gb').

Available parameters:
- 'source' (required): The location code for the departure point.
- 'source_type' (optional): Type of the source location. Can be 'City', 'Country', 'Airport'. Defaults to 'City'.
- 'destination' (required): The location code for the arrival point.
- 'destination_type' (optional): Type of the destination. Can be 'City', 'Country', 'Airport'. Defaults to 'City'.
- 'departure_start_date': The earliest departure date in 'YYYY-MM-DD' format. Defaults to tomorrow.
- 'departure_end_date': The latest departure date in 'YYYY-MM-DD' format. Defaults to 7 days from now.
- 'inbound_start_date': The earliest return date in 'YYYY-MM-DD' format. Providing this parameter triggers a round-trip search.
- 'inbound_end_date': The latest return date in 'YYYY-MM-DD' format.
- 'adults': Number of adults. Defaults to 1.
- 'children': Number of children. Defaults to 0.
- 'infants': Number of infants. Defaults to 0.
- 'currency': The currency for the price, e.g., 'USD', 'EUR', 'PLN'. Defaults to 'USD'.
- 'sortBy': Sorting criteria. Can be 'PRICE', 'QUALITY', 'DATE'. Defaults to 'PRICE'.
- 'cabinClass': Travel class. Can be 'ECONOMY', 'PREMIUM_ECONOMY', 'BUSINESS', 'FIRST'. Defaults to 'ECONOMY'.
- 'limit': Maximum number of results to return. Defaults to 1.

The tool returns a JSON list of available flight options, including price, provider, flight times, and a booking link.""",
    func=search_flights
)
