from fastapi import APIRouter, HTTPException
from api.models import TripBase, TripDB, PyObjectId
from typing import List
from core.database import trips_col
from core.database import messages_col

router = APIRouter(prefix="/trips", tags=["Trips"])

@router.post("/", response_model=TripDB)
async def create_trip(trip: TripBase):
    trip_dict = trip.model_dump(by_alias=True)
    result = await trips_col.insert_one(trip_dict)
    new_trip = await trips_col.find_one({"_id": result.inserted_id})

    if not new_trip:
        raise HTTPException(status_code=500, detail="Failed to retrieve created trip")
    
    new_trip["_id"] = str(new_trip["_id"])
    new_trip["user_id"] = str(new_trip["user_id"])
    return new_trip


@router.get("/{trip_id}", response_model=TripDB)
async def get_trip(trip_id: str):
    try:
        object_id = PyObjectId(trip_id)
        trip = await trips_col.find_one({"_id": object_id})
        trip["_id"] = str(trip["_id"])
        trip["user_id"] = str(trip["user_id"])
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

        return trips

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
