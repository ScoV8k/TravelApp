from fastapi import APIRouter, HTTPException
from api.models import MessageBase, MessageDB, PyObjectId
from typing import List
from core.database import messages_col

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post("/", response_model=MessageDB)
async def create_message(msg: MessageBase):
    msg_dict = msg.model_dump(by_alias=True)
    result = await messages_col.insert_one(msg_dict)
    
    new_msg = await messages_col.find_one({"_id": result.inserted_id})
    if not new_msg:
        raise HTTPException(status_code=500, detail="Failed to retrieve created message")

    new_msg["_id"] = str(new_msg["_id"])
    new_msg["trip_id"] = str(new_msg["trip_id"])
    return new_msg


@router.get("/trip/{trip_id}", response_model=List[MessageDB])
async def get_messages_for_trip(trip_id: str):
    try:
        object_id = PyObjectId(trip_id) 
        messages_cursor = messages_col.find({"trip_id": object_id})
        messages = await messages_cursor.to_list(length=100)

        for msg in messages:
            msg["_id"] = str(msg["_id"])
            msg["trip_id"] = str(msg["trip_id"])

        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve messages: {str(e)}")
