from fastapi import APIRouter, HTTPException, Body
from api.models import TripBase, TripDB, PyObjectId
from typing import List
from core.database import trips_col, plans_col, trips_information_col
from travelplan.traveljson import get_empty_travel_information


router = APIRouter(prefix="/trips", tags=["Trips"])


@router.post("/", response_model=TripDB)
async def create_trip(trip: TripBase):
    from core.database import trips_information_col
    from datetime import datetime

    trip_dict = trip.model_dump(by_alias=True)
    trip_dict["information_id"] = None
    trip_dict["plan_id"] = None
    result = await trips_col.insert_one(trip_dict)

    try:
        empty_plan = get_empty_travel_information()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nie udało się wygenerować szkieletu planu: {str(e)}")

    trip_id = result.inserted_id
    information_doc = {
        "trip_id": trip_id,
        "data": empty_plan,
        "updated_at": datetime.utcnow(),
        "checklist": []
    }
    information_result = await trips_information_col.insert_one(information_doc)
    information_id = information_result.inserted_id

    plan_doc = {
        "trip_id": trip_id,
        "data": {"status": "empty"},
        "updated_at": datetime.utcnow(),
    }
    plan_result = await plans_col.insert_one(plan_doc)
    plan_id = plan_result.inserted_id

    await trips_col.update_one(
        {"_id": trip_id},
        {"$set": {"information_id": information_id}}
    )

    await trips_col.update_one(
        {"_id": trip_id},
        {"$set": {"plan_id": plan_id}}
    )

    new_trip = await trips_col.find_one({"_id": trip_id})
    if not new_trip:
        raise HTTPException(status_code=500, detail="Failed to retrieve created trip")

    # Konwersja do str tylko jeśli wartość nie jest None
    def safe_str(val):
        return str(val) if val is not None else None

    new_trip["_id"] = safe_str(new_trip["_id"])
    new_trip["user_id"] = safe_str(new_trip["user_id"])
    new_trip["information_id"] = safe_str(information_id)
    new_trip["plan_id"] = safe_str(new_trip.get("plan_id"))

    return new_trip


@router.get("/{trip_id}", response_model=TripDB)
async def get_trip(trip_id: str):
    try:
        object_id = PyObjectId(trip_id)
        trip = await trips_col.find_one({"_id": object_id})
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        def safe_str(val):
            return str(val) if val is not None else None

        trip["_id"] = safe_str(trip["_id"])
        trip["user_id"] = safe_str(trip["user_id"])
        trip["information_id"] = safe_str(trip.get("information_id"))
        trip["plan_id"] = safe_str(trip.get("plan_id"))

        return trip
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")


@router.get("/status/{trip_id}")
async def get_trip(trip_id: str):
    try:
        object_id = PyObjectId(trip_id)
        trip = await trips_col.find_one({"_id": object_id})
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")

        def safe_str(val):
            return str(val) if val is not None else None

        # trip_status = safe_str(trip.get("status"))

        return {"status": trip.get("status", "draft")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")


@router.get("/user/{user_id}", response_model=List[TripDB])
async def get_trips_by_user(user_id: str):
    try:
        user_object_id = PyObjectId(user_id)
        trips_cursor = trips_col.find({"user_id": user_object_id})
        trips = await trips_cursor.to_list(length=100)

        def safe_str(val):
            return str(val) if val is not None else None

        for trip in trips:
            trip["_id"] = safe_str(trip["_id"])
            trip["user_id"] = safe_str(trip["user_id"])
            trip["information_id"] = safe_str(trip.get("information_id"))
            trip["plan_id"] = safe_str(trip.get("plan_id"))

        return trips

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trips: {str(e)}")


@router.patch("/{trip_id}", response_model=TripDB)
async def update_trip_name(trip_id: str, data: dict = Body(...)):
    try:
        object_id = PyObjectId(trip_id)

        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]

        if "plan_id" in data:
            plan_val = data["plan_id"]
            update_data["plan_id"] = PyObjectId(plan_val) if plan_val else None

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        result = await trips_col.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Trip not found")

        updated_trip = await trips_col.find_one({"_id": object_id})

        def safe_str(val):
            return str(val) if val is not None else None

        updated_trip["_id"] = safe_str(updated_trip["_id"])
        updated_trip["user_id"] = safe_str(updated_trip["user_id"])
        updated_trip["information_id"] = safe_str(updated_trip.get("information_id"))
        updated_trip["plan_id"] = safe_str(updated_trip.get("plan_id"))

        return updated_trip

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating trip: {str(e)}")



@router.delete("/{trip_id}")
async def delete_trip(trip_id: str):
    """
    Usuń trip o danym ID wraz z powiązanymi dokumentami:
    - trips
    - trips_information_col
    - plans_col
    """
    try:
        object_id = PyObjectId(trip_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {e}")

    # najpierw sprawdź czy istnieje
    existing = await trips_col.find_one({"_id": object_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Trip not found")

    # usuń główny dokument
    await trips_col.delete_one({"_id": object_id})
    # usuń powiązaną informację
    await trips_information_col.delete_many({"trip_id": object_id})
    # usuń powiązany plan
    await plans_col.delete_many({"trip_id": object_id})

    # zwracamy 204 No Content
    return None