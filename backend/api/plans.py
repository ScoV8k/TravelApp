from fastapi import APIRouter, HTTPException, Body
from api.models import PlanBase, PlanDB, PyObjectId # Assuming these models are in api.models
from typing import List
from core.database import plans_col # Assuming a new collection for plans
from datetime import datetime
from bson import ObjectId # Import ObjectId for type hinting if needed, though PyObjectId handles it

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.post("/", response_model=PlanDB)
async def create_plan(plan: PlanBase):
    # 1. Prepare the plan data for insertion
    # model_dump(by_alias=True) handles converting PyObjectId to ObjectId for MongoDB
    plan_dict = plan.model_dump(by_alias=True)

    # Ensure updated_at is current, even if provided in the input,
    # to reflect the exact creation time in the database.
    plan_dict["updated_at"] = datetime.utcnow()
    print(plan_dict)
    # 2. Insert the plan document into the plans collection
    try:
        result = await plans_col.insert_one(plan_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert plan into database: {str(e)}")

    # Get the ID of the newly inserted plan
    plan_id = result.inserted_id

    # 3. Retrieve the newly created plan from the database
    # This step ensures we return the full document as stored, including the _id.
    new_plan = await plans_col.find_one({"_id": plan_id})

    if not new_plan:
        raise HTTPException(status_code=500, detail="Failed to retrieve the newly created plan")

    # 4. Convert ObjectId fields to string for the Pydantic response model
    # Pydantic's json_encoders will handle ObjectId to str conversion automatically
    # if configured correctly, but explicit conversion here ensures consistency
    # with how TripDB handles its _id and user_id.
    new_plan["_id"] = str(new_plan["_id"])
    new_plan["trip_id"] = str(new_plan["trip_id"]) # Ensure trip_id is also a string

    return new_plan