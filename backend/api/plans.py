from fastapi import APIRouter, HTTPException, Body
from api.models import PlanBase, PlanDB, PyObjectId
from core.database import plans_col
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/plans", tags=["Plans"])


@router.post("/", response_model=PlanDB)
async def create_plan(plan: PlanBase):
    plan_dict = plan.model_dump(by_alias=True)

    plan_dict["updated_at"] = datetime.utcnow()

    try:
        result = await plans_col.insert_one(plan_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert plan: {str(e)}")

    new_plan = await plans_col.find_one({"_id": result.inserted_id})
    if not new_plan:
        raise HTTPException(status_code=500, detail="Failed to retrieve newly created plan")

    new_plan["_id"] = str(new_plan["_id"])
    new_plan["trip_id"] = str(new_plan["trip_id"])

    return new_plan


@router.put("/{plan_id}", response_model=PlanDB)
async def update_plan(plan_id: str, plan: PlanBase):
    """
    Update an existing plan by its ID.
    """
    plan_dict = plan.model_dump(by_alias=True)
    plan_dict["updated_at"] = datetime.utcnow()

    result = await plans_col.update_one(
        {"_id": ObjectId(plan_id)},
        {"$set": plan_dict}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found or no changes made")

    updated_plan = await plans_col.find_one({"_id": ObjectId(plan_id)})
    updated_plan["_id"] = str(updated_plan["_id"])
    updated_plan["trip_id"] = str(updated_plan["trip_id"])

    return updated_plan

@router.get("/{trip_id}", response_model=PlanDB)
async def get_plan_by_trip_id(trip_id: str):
    try:
        trip_object_id = PyObjectId(trip_id)
        plan = await plans_col.find_one({"trip_id": trip_object_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        plan["_id"] = str(plan["_id"])
        plan["trip_id"] = str(plan["trip_id"])

        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plan: {str(e)}")

