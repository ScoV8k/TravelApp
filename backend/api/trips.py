from fastapi import APIRouter, HTTPException, Body
from api.models import TripBase, TripDB, PyObjectId
from typing import List
from core.database import trips_col
from core.database import messages_col
from travelplan.traveljson import get_empty_plan


router = APIRouter(prefix="/trips", tags=["Trips"])
@router.post("/", response_model=TripDB)
async def create_trip(trip: TripBase):
    from core.database import plans_col
    from datetime import datetime

    # 1. Stworzenie tripa bez plan_id
    trip_dict = trip.model_dump(by_alias=True)
    trip_dict["plan_id"] = None
    result = await trips_col.insert_one(trip_dict)

    # 2. Pobierz szkielet planu z funkcji
    try:
        empty_plan = get_empty_plan()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nie udało się wygenerować szkieletu planu: {str(e)}")

    # 3. Tworzymy plan z szablonem
    trip_id = result.inserted_id
    plan_doc = {
        "trip_id": trip_id,
        "data": empty_plan,
        "updated_at": datetime.utcnow(),
        "checklist": []
    }
    plan_result = await plans_col.insert_one(plan_doc)
    plan_id = plan_result.inserted_id

    # 4. Aktualizacja tripa o plan_id
    await trips_col.update_one(
        {"_id": trip_id},
        {"$set": {"plan_id": plan_id}}
    )

    # 5. Zwracamy nowo utworzony trip
    new_trip = await trips_col.find_one({"_id": trip_id})
    if not new_trip:
        raise HTTPException(status_code=500, detail="Failed to retrieve created trip")
    
    new_trip["_id"] = str(new_trip["_id"])
    new_trip["user_id"] = str(new_trip["user_id"])
    new_trip["plan_id"] = str(plan_id)
    return new_trip



@router.get("/{trip_id}", response_model=TripDB)
async def get_trip(trip_id: str):
    try:
        object_id = PyObjectId(trip_id)
        trip = await trips_col.find_one({"_id": object_id})
        trip["_id"] = str(trip["_id"])
        trip["user_id"] = str(trip["user_id"])
        trip["plan_id"] = str(trip["plan_id"])
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        return trip
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")

@router.get("/user/{user_id}", response_model=List[TripDB])
async def get_trips_by_user(user_id: str):
    try:
        user_object_id = PyObjectId(user_id)
        trips_cursor = trips_col.find({"user_id": user_object_id})
        trips = await trips_cursor.to_list(length=100)

        for trip in trips:
            trip["_id"] = str(trip["_id"])
            trip["user_id"] = str(trip["user_id"])
            trip["plan_id"] = str(trip["plan_id"])

        return trips

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve trips: {str(e)}")



@router.delete("/{trip_id}")
async def delete_trip(trip_id: str):
    try:
        object_id = PyObjectId(trip_id)

        delete_result = await trips_col.delete_one({"_id": object_id})
        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        await messages_col.delete_many({"trip_id": object_id})

        return {"message": "Trip and associated messages deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting trip: {str(e)}")


@router.patch("/{trip_id}", response_model=TripDB)
async def update_trip_name(trip_id: str, data: dict = Body(...)):
    try:
        object_id = PyObjectId(trip_id)

        update_data = {}
        if "name" in data:
            update_data["name"] = data["name"]

        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")

        result = await trips_col.update_one(
            {"_id": object_id},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Trip not found or not modified")

        updated_trip = await trips_col.find_one({"_id": object_id})
        updated_trip["_id"] = str(updated_trip["_id"])
        updated_trip["user_id"] = str(updated_trip["user_id"])

        return updated_trip

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating trip: {str(e)}")