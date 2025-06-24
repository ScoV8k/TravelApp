from fastapi import APIRouter, HTTPException
from api.models import UserBase, UserDB, PyObjectId, AboutMeUpdate
from core.security import hash_password
from core.database import users_col

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserDB)
async def create_user(user: UserBase):
    user_dict = user.model_dump()

    if "password" in user_dict:
        user_dict["password"] = hash_password(user_dict["password"])
    
    result = await users_col.insert_one(user_dict)
    
    new_user = await users_col.find_one({"_id": result.inserted_id})
    if not new_user:
        raise HTTPException(status_code=500, detail="Failed to retrieve created user")
    
    new_user["_id"] = str(new_user["_id"])
    return new_user


@router.get("/{user_id}", response_model=UserDB)
async def get_user(user_id: str):
    try:
        object_id = PyObjectId(user_id)
        user = await users_col.find_one({"_id": object_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user["_id"] = str(user["_id"])
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {str(e)}")
    

@router.get("/by-name/{user_name}", response_model=UserDB)
async def get_user_by_name(user_name: str):
    user = await users_col.find_one({"name": user_name})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user["_id"] = str(user["_id"])
    return user

@router.put("/{user_id}/about", status_code=204)
async def update_about_me(user_id: str, payload: AboutMeUpdate):
    try:
        object_id = PyObjectId(user_id)
        result = await users_col.update_one(
            {"_id": object_id},
            {"$set": {"about": payload.about}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return 

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid ID format or other error: {str(e)}")
