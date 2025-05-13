def get_empty_plan():
    return {
        "destination_country": None,
        "destination_cities": [],
        "start_date": None,
        "end_date": None,
        "duration_days": None,
        "travelers_details": [
            {
                "name": None,
                "age": None,
                "preferences": None
            }
        ],
        "accommodation": [
            {
                "city": None,
                "check_in": None,
                "check_out": None,
                "chosen_hotel": None,
                "suggested_hotels": []
            }
        ],
        "places_to_visit": [
            {
                "city": None,
                "suggested_places": [],
                "user_selected": []
            }
        ],
        "activities": [
            {
                "type": None,
                "description": None,
                "location": None,
                "suggested_options": []
            }
        ],
        "budget": {
            "estimated_total": None,
            "categories": {
                "transport": None,
                "accommodation": None,
                "food": None,
                "activities": None
            },
            "currency": None
        },
        "additional_notes": [
            {
                "text": None
            }
        ]
    }
