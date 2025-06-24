from pydantic import BaseModel, Field
from typing import Optional, List, Any
from bson import ObjectId
from datetime import datetime

from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema
from typing import Any


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler: GetJsonSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            try:
                return ObjectId(v)
            except Exception:
                raise ValueError("Invalid ObjectId")
        raise TypeError("ObjectId required")



class UserBase(BaseModel):
    name: str
    email: str
    password: str
    about: Optional[str] = Field(None, max_length=400)

class UserDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: str
    password: str
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class AboutMeUpdate(BaseModel):
    about: str = Field(..., max_length=400)

# TRIPS
class TripBase(BaseModel):
    user_id: PyObjectId
    name: str
    created_at: datetime
    status: str

    class Config:
        json_encoders = {ObjectId: str}


class TripDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    information_id: PyObjectId  # tylko w zwracanym modelu z bazy
    name: str
    created_at: datetime
    status: str
    plan_id: Optional[PyObjectId] = None


    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True



# MESSAGES
class MessageBase(BaseModel):
    trip_id: PyObjectId
    text: str
    isUser: bool
    timestamp: datetime

    class Config:
        json_encoders = {ObjectId: str}

class MessageDB(MessageBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    trip_id: PyObjectId
    text: str
    isUser: bool
    timestamp: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ChecklistItem(BaseModel):
    id: int
    name: str
    checked: bool = False

class Checklist(BaseModel):
    id: int
    name: str
    items: List[ChecklistItem] = []


# Plan
class TripInformationBase(BaseModel):
    trip_id: PyObjectId
    data: dict
    updated_at: datetime
    checklist: List[Checklist]

    class Config:
        json_encoders = {ObjectId: str}

class TripInformationDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    trip_id: PyObjectId
    data: dict
    updated_at: datetime
    checklist: List[Checklist]

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


# Plan
class PlanBase(BaseModel):
    trip_id: PyObjectId
    data: dict
    updated_at: datetime

    class Config:
        json_encoders = {ObjectId: str}

class PlanDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    trip_id: PyObjectId
    data: dict
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True

