from fastapi import APIRouter, HTTPException, Body
from api.models import PlanBase, PlanDB, PyObjectId, ChecklistItem
from core.database import plans_col
from datetime import datetime
from typing import List


router = APIRouter(prefix="/plans", tags=["Plans"])

@router.post("/", response_model=PlanDB)
async def create_plan(plan: PlanBase):
    plan_dict = plan.model_dump(by_alias=True)
    result = await plans_col.insert_one(plan_dict)
    new_plan = await plans_col.find_one({"_id": result.inserted_id})

    if not new_plan:
        raise HTTPException(status_code=500, detail="Failed to retrieve created plan")

    new_plan["_id"] = str(new_plan["_id"])
    new_plan["trip_id"] = str(new_plan["trip_id"])
    return new_plan

@router.get("/trip/{trip_id}", response_model=PlanDB)
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

@router.patch("/trip/{trip_id}", response_model=PlanDB)
async def update_plan_by_trip_id(trip_id: str, data: dict = Body(...)):
    try:
        trip_object_id = PyObjectId(trip_id)
        result = await plans_col.update_one(
            {"trip_id": trip_object_id},
            {"$set": {"data": data, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found or not modified")

        updated_plan = await plans_col.find_one({"trip_id": trip_object_id})
        updated_plan["_id"] = str(updated_plan["_id"])
        updated_plan["trip_id"] = str(updated_plan["trip_id"])
        return updated_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating plan: {str(e)}")

@router.delete("/trip/{trip_id}")
async def delete_plan_by_trip_id(trip_id: str):
    try:
        trip_object_id = PyObjectId(trip_id)
        result = await plans_col.delete_one({"trip_id": trip_object_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found")

        return {"message": "Plan deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting plan: {str(e)}")



@router.patch("/trip/{trip_id}/checklist", response_model=PlanDB)
async def update_checklist_by_trip_id(trip_id: str, checklist: List[ChecklistItem]):
    try:
        trip_object_id = PyObjectId(trip_id)
        result = await plans_col.update_one(
            {"trip_id": trip_object_id},
            {"$set": {"checklist": [item.dict() for item in checklist], "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found or not modified")

        updated_plan = await plans_col.find_one({"trip_id": trip_object_id})
        updated_plan["_id"] = str(updated_plan["_id"])
        updated_plan["trip_id"] = str(updated_plan["trip_id"])
        return updated_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating checklist: {str(e)}")

# --- 3. Endpoint GET checklisty dla tripa ---

@router.get("/trip/{trip_id}/checklist", response_model=List[ChecklistItem])
async def get_checklist_by_trip_id(trip_id: str):
    try:
        trip_object_id = PyObjectId(trip_id)
        plan = await plans_col.find_one({"trip_id": trip_object_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan.get("checklist", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving checklist: {str(e)}")


