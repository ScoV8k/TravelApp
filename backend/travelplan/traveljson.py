def get_empty_travel_information():
    return {
        "destination_countries": [],
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
                "chosen_hotel": None
            }
        ],
        "places_to_visit": [
            {
                "city": None,
                "duration_days": None,
                "activities": [
                    {
                    "name": None,
                    "type": None,
                    "description": None,
                    "location": None
                    }
                ],
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
          "location_name": None,
          "description": None,
          "type": None,
          "tags": None
        }
      ],
      "notes": None
    }
  ],
  "general_notes": [],
  "emergency_contacts": [
    {
        "name": None,
        "phone": None,
        "type": None  # np. "embassy", "local police", "travel agent"
    }
]

}"""
