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


def get_empty_plan2():
    return """{
  "trip_name": None,
  "start_date": None,
  "end_date": None,
  "duration_days": None,
  "destination_country": None,
  "destination_cities": [],
  "daily_plan": [
    {
      "day": None,
      "date": None,
      "city": None,
      "summary": None,
      "accommodation": {
        "hotel_name": None,
        "check_in": None,
        "address": None
      },
      "activities": [
        {
          "time": None,
          "title": None,
          "description": None,
          "location": {
            "name": None,
            "lat": None,
            "lng": None
          },
          "type": None,
          "map_link": None
        }
      ],
      "notes": None
    }
  ],
  "map_summary": {
    "locations": [
      {
        "name": None,
        "lat": None,
        "lng": None,
        "day": None,
        "type": None
      }
    ]
  },
  "general_notes": []
}"""
