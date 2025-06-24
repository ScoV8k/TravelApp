from fastapi import APIRouter, HTTPException, Body
from api.models import  PyObjectId, Checklist, TripInformationDB, TripInformationBase
from core.database import trips_information_col
from datetime import datetime
from typing import List


router = APIRouter(prefix="/information", tags=["Information"])

@router.post("/", response_model=TripInformationDB)
async def create_plan(plan: TripInformationBase):
    plan_dict = plan.model_dump(by_alias=True)
    result = await trips_information_col.insert_one(plan_dict)
    new_plan = await trips_information_col.find_one({"_id": result.inserted_id})

    if not new_plan:
        raise HTTPException(status_code=500, detail="Failed to retrieve created plan")

    new_plan["_id"] = str(new_plan["_id"])
    new_plan["trip_id"] = str(new_plan["trip_id"])
    return new_plan

@router.get("/trip/{trip_id}", response_model=TripInformationDB)
async def get_plan_by_trip_id(trip_id: str):
    try:
        trip_object_id = PyObjectId(trip_id)
        plan = await trips_information_col.find_one({"trip_id": trip_object_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        plan["_id"] = str(plan["_id"])
        plan["trip_id"] = str(plan["trip_id"])
        return plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving plan: {str(e)}")

@router.patch("/trip/{trip_id}", response_model=TripInformationDB)
async def update_plan_by_trip_id(trip_id: str, data: dict = Body(...)):
    try:
        trip_object_id = PyObjectId(trip_id)
        result = await trips_information_col.update_one(
            {"trip_id": trip_object_id},
            {"$set": {"data": data, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found or not modified")

        updated_plan = await trips_information_col.find_one({"trip_id": trip_object_id})
        updated_plan["_id"] = str(updated_plan["_id"])
        updated_plan["trip_id"] = str(updated_plan["trip_id"])
        return updated_plan
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating plan: {str(e)}")

@router.delete("/trip/{trip_id}")
async def delete_plan_by_trip_id(trip_id: str):
    try:
        trip_object_id = PyObjectId(trip_id)
        result = await trips_information_col.delete_one({"trip_id": trip_object_id})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Plan not found")

        return {"message": "Plan deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting plan: {str(e)}")


@router.get("/trip/{trip_id}/checklists", response_model=List[Checklist])
async def get_checklists(trip_id: str):
    trip_object_id = PyObjectId(trip_id)
    plan = await trips_information_col.find_one({"trip_id": trip_object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    checklists = plan.get("checklist", [])
    return checklists


@router.post("/trip/{trip_id}/checklists/add", response_model=List[Checklist])
async def add_checklist(trip_id: str, data: dict = Body(...)):
    trip_object_id = PyObjectId(trip_id)
    plan = await trips_information_col.find_one({"trip_id": trip_object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    checklists = plan.get("checklist", [])

    max_id = max([c["id"] for c in checklists], default=0)
    
    
    new_checklist = {
        "id": max_id + 1,
        "name": data.get("name"),
        "items": []
    }

    checklists.append(new_checklist)

    await trips_information_col.update_one(
        {"trip_id": trip_object_id},
        {"$set": {"checklist": checklists, "updated_at": datetime.utcnow()}}
    )

    return checklists


@router.post("/trip/{trip_id}/checklists/{checklist_id}/items/add", response_model=List[Checklist])
async def add_checklist_item(trip_id: str, checklist_id: int, item: dict = Body(...)):
    trip_object_id = PyObjectId(trip_id)
    plan = await trips_information_col.find_one({"trip_id": trip_object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    checklists = plan.get("checklist", [])

    for checklist in checklists:
        if checklist["id"] == checklist_id:
            items = checklist.get("items", [])
            max_item_id = max([i["id"] for i in items], default=0)
            new_item = {
                "id": max_item_id + 1,
                "name": item.get("name"),
                "checked": False
            }
            items.append(new_item)
            checklist["items"] = items
            break
    else:
        raise HTTPException(status_code=404, detail="Checklist not found")

    await trips_information_col.update_one(
        {"trip_id": trip_object_id},
        {"$set": {"checklist": checklists, "updated_at": datetime.utcnow()}}
    )

    return checklists


@router.patch("/trip/{trip_id}/checklists/{checklist_id}/items/{item_id}", response_model=List[Checklist])
async def toggle_checklist_item(trip_id: str, checklist_id: int, item_id: int, checked: bool = Body(...)):
    trip_object_id = PyObjectId(trip_id)
    plan = await trips_information_col.find_one({"trip_id": trip_object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    checklists = plan.get("checklist", [])
    for checklist in checklists:
        if checklist["id"] == checklist_id:
            for item in checklist["items"]:
                if item["id"] == item_id:
                    item["checked"] = checked
                    break
            else:
                raise HTTPException(status_code=404, detail="Item not found")
            break
    else:
        raise HTTPException(status_code=404, detail="Checklist not found")

    await trips_information_col.update_one(
        {"trip_id": trip_object_id},
        {"$set": {"checklist": checklists, "updated_at": datetime.utcnow()}}
    )

    return checklists


@router.delete("/trip/{trip_id}/checklists/{checklist_id}", response_model=List[Checklist])
async def delete_checklist(trip_id: str, checklist_id: int):
    trip_object_id = PyObjectId(trip_id)
    plan = await trips_information_col.find_one({"trip_id": trip_object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    checklists = plan.get("checklist", [])
    
    updated_checklists = [cl for cl in checklists if cl.get("id") != checklist_id]

    if len(updated_checklists) == len(checklists):
        raise HTTPException(status_code=404, detail="Checklist not found")

    await trips_information_col.update_one(
        {"trip_id": trip_object_id},
        {"$set": {"checklist": updated_checklists, "updated_at": datetime.utcnow()}}
    )

    return updated_checklists

@router.delete("/trip/{trip_id}/checklists/{checklist_id}/items/{item_id}", response_model=List[Checklist])
async def delete_checklist_item(trip_id: str, checklist_id: int, item_id: int):
    trip_object_id = PyObjectId(trip_id)
    plan = await trips_information_col.find_one({"trip_id": trip_object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    checklists = plan.get("checklist", [])
    checklist_found = False
    item_found = False

    for checklist in checklists:
        if checklist.get("id") == checklist_id:
            checklist_found = True
            original_items = checklist.get("items", [])
            updated_items = [item for item in original_items if item.get("id") != item_id]
            
            if len(updated_items) < len(original_items):
                item_found = True
                checklist["items"] = updated_items
            break
            
    if not checklist_found:
        raise HTTPException(status_code=404, detail="Checklist not found")
    if not item_found:
        raise HTTPException(status_code=404, detail="Item not found")

    await trips_information_col.update_one(
        {"trip_id": trip_object_id},
        {"$set": {"checklist": checklists, "updated_at": datetime.utcnow()}}
    )

    return checklists
