from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from datetime import datetime
from bson import ObjectId
from core.database import plans_col, trips_col, users_col
from api.models import PlanDB
import json
import os
from typing import List, Dict
from fastapi import BackgroundTasks
from core.database import trips_information_col
from travelplan.traveljson import get_empty_plan2
from dotenv import load_dotenv
import asyncio
import googlemaps

load_dotenv()
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

async def enrich_place_with_googlemaps_client(place_name: str, city: str):
    if not gmaps:
        raise ValueError("Google Maps client is not initialized")

    find_result = gmaps.find_place(
        input= place_name + ", " + city,
        input_type="textquery",
        fields=[
            "place_id", 
            "name", 
            "formatted_address", 
            "geometry",
            "photos" 
        ]
    )
    
    candidates = find_result.get("candidates", [])
    if not candidates:
        print(f"Nie znaleziono kandydatów dla: {place_name}")
        return None
    result = candidates[0]

    place_id = candidates[0]["place_id"]
    # photo_url = None
    photos = result.get("photos")
    if photos:
        photo_reference = photos[0].get("photo_reference")
        # if photo_reference:
        #     photo_url = get_place_photo_url(photo_reference)

    return {
        "place_id": place_id,
        "name": result.get("name", place_name),
        "formatted_address": result.get("formatted_address", ""),
        "lat": result.get("geometry", {}).get("location", {}).get("lat"),
        "lng": result.get("geometry", {}).get("location", {}).get("lng"),
        "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
        # "photo_url": photo_url
        "photo_reference": photo_reference
    }



async def enrich_plan_with_locations(plan_data: dict) -> dict:
    for day in plan_data.get("daily_plan", []):
        city = day.get("city")
        for activity in day.get("activities", []):
            place_name = activity.get("location_name")
            if place_name and ("lat" not in activity or "lng" not in activity):
                enriched = await enrich_place_with_googlemaps_client(place_name, city)
                if enriched:
                    activity.update({
                    "place_id": enriched["place_id"],
                    "lat": enriched["lat"],
                    "lng": enriched["lng"],
                    "formatted_address": enriched["formatted_address"],
                    # "google_maps_url": enriched["google_maps_url"],
                    "maps_url": enriched["google_maps_url"],
                    # "photo_url": enriched.get("photo_url")
                    "photo_reference": enriched["photo_reference"]
                })


    return plan_data


def get_place_photo_url(photo_reference: str, maxwidth: int = 800):
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={maxwidth}&photoreference={photo_reference}&key={os.getenv('GOOGLE_MAPS_API_KEY')}"



# Model rozmowy
chat_llm = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.7,
    max_tokens=512
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

chat_llm_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly travel assistant. Your task is to help the user plan a trip by asking one question at a time. Ask specific, small questions to gradually gather details. Do NOT propose or generate a full trip plan. Only ask questions like: 'Where do you want to go?', 'What dates are you planning?', 'What kind of places do you like?', 'What’s your budget?', etc."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{message}"),
])

chat_chain = LLMChain(llm=chat_llm, prompt=chat_llm_prompt, memory=memory)





# Model zbierania informacji
information_llm = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.7,
    max_tokens=512
)

information_llm_prompt = PromptTemplate(
    input_variables=["last_user_message", "message_history", "current_plan"],
    template="""
You are a travel plan updater.

Your task is to update the existing travel plan JSON **only based on the last user answer**. 
Use the conversation history **only for context** if needed, but do not use assistant messages as source of truth.

- Make only minimal and necessary edits.
- If information is missing, leave it empty.
- Output must be a valid, complete JSON.

Last user answer:
{last_user_message}

Conversation history (last 3 messages for context):
{message_history}

Current plan JSON:
{current_plan}

Updated plan JSON:
"""
)

information_update_chain = LLMChain(llm=information_llm, prompt=information_llm_prompt)
json2_skeleton = get_empty_plan2()




# Model generowania planu
plan_generator_llm = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0.7,
    max_tokens=4096
)

plan_generator_llm_prompt = PromptTemplate(
    input_variables=["travel_information", "json2_skeleton"],
    template="""
Generate a short travel plan based on the data from TRAVEL INFORMATION.
Fill in the plan in JSON. If any data is missing – add your own interesting suggestions for attractions.

🔴 VERY IMPORTANT:
- RETURN ONLY A VALID AND CLEAN JSON – NO COMMENTS, NO TEXT BEFORE OR AFTER.
- The JSON must be syntactically correct (parsable with the json.loads function in Python).
- Make sure EVERY element in a list or object is SEPARATED by a comma (,).
- DO NOT use a comma after the last element of a list or object.
- NEWLINE characters inside strings should be written as \\n (double backslash).

TRAVEL INFORMATION:
{travel_information}

JSON:
{json2_skeleton}
""" 
# + json2_skeleton
)

plan_generator_chain = LLMChain(llm=plan_generator_llm, prompt=plan_generator_llm_prompt)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TematRequest(BaseModel):
    message: str

class PromptRequest(BaseModel):
    prompt: str

class TripInformationUpdateRequest(BaseModel):
    trip_id: str
    last_user_message: str
    bot_response: str


class Demo(BaseModel):
    trip_id: str
    user_message: str
    last_messages: List[Dict]

@app.post("/generate/")
async def generate_response(req: TematRequest):
    result = await chat_chain.arun(message=req.message)
    return {"message": req.message, "response": result}


async def try_parse_json(response_text: str, retries: int = 2):
    """Try parsing JSON with retries and fixes"""
    for attempt in range(retries + 1):
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
            return json.loads(json_str)
        except Exception as e:
            print(f"🔴 JSON parsing error (attempt {attempt + 1}): {str(e)}")
            if attempt == retries:
                raise HTTPException(status_code=500, detail=f"JSON Error: {str(e)}")
            await asyncio.sleep(1)



# @app.post("/generate-plan/{trip_id}", response_model=PlanDB)
# async def generate_and_save_plan(trip_id: str):
#     plan_doc = await trips_information_col.find_one({"trip_id": ObjectId(trip_id)})
#     if not plan_doc:
#         raise HTTPException(status_code=404, detail="Plan source data not found")

#     travel_information = plan_doc.get("data", {})

@app.post("/generate-plan/{trip_id}", response_model=PlanDB)
async def generate_and_save_plan(trip_id: str):
    trip_main_doc = await trips_col.find_one({"_id": ObjectId(trip_id)})
    if not trip_main_doc:
        raise HTTPException(status_code=404, detail="Trip not found")

    user_id = trip_main_doc.get("user_id")

    user_about_info = ""
    if user_id:
        try:
            user_doc = await users_col.find_one({"_id": ObjectId(user_id)})
            if user_doc and "about" in user_doc:
                user_about_info = user_doc["about"]
                print(f"🟢 Found user preferences for user_id: {user_id}")
        except Exception as e:
            print(f"⚠️ Could not fetch user info for user_id: {user_id}. Error: {e}")

    plan_info_doc = await trips_information_col.find_one({"trip_id": ObjectId(trip_id)})
    if not plan_info_doc:
        raise HTTPException(status_code=404, detail="Plan source data not found")

    travel_information = plan_info_doc.get("data", {})

    raw_prompt = f"""
Generate a short travel plan based on the data from TRAVEL INFORMATION.
Fill in the plan in JSON. If any data is missing – add your own interesting suggestions for attractions.

🔴 VERY IMPORTANT:
- RETURN ONLY A VALID AND CLEAN JSON – NO COMMENTS, NO TEXT BEFORE OR AFTER.
- The JSON must be syntactically correct (parsable with the json.loads function in Python).
- Make sure EVERY element in a list or object is SEPARATED by a comma (,).
- DO NOT use a comma after the last element of a list or object.
- NEWLINE characters inside strings should be written as \\n (double backslash).

TRAVEL INFORMATION:
{json.dumps(travel_information, indent=2)}

INFORMATION FROM USER:
{user_about_info}

JSON:
{json2_skeleton}
""" 

    response = await plan_generator_llm.ainvoke(raw_prompt)
#     response = await plan_generator_chain.arun(
#     travel_information=json.dumps(travel_information),
#     json2_skeleton=json2_skeleton
# )
    response_text = response.content
    print(f"🟢 Raw model response:\n{response_text}\n")

    print("RAW PROMPT: ", raw_prompt)

    plan_data = await try_parse_json(response_text, retries=2)

    enriched_plan = await enrich_plan_with_locations(plan_data)
    print("enriched plan!!!: ", enriched_plan)
    plan_doc = {
        "trip_id": ObjectId(trip_id),
        "data": enriched_plan,
        "updated_at": datetime.utcnow()
    }
    await plans_col.replace_one(
        {"trip_id": ObjectId(trip_id)},
        plan_doc,
        upsert=True
    )

    await trips_col.update_one(
        {"_id": ObjectId(trip_id)},
        {"$set": {"status": "planned"}}
    )

    new_plan = await plans_col.find_one({"trip_id": ObjectId(trip_id)})
    if not new_plan:
        raise HTTPException(status_code=500, detail="Failed to store generated plan")

    new_plan["_id"] = str(new_plan["_id"])
    new_plan["trip_id"] = str(new_plan["trip_id"])

    return new_plan




@app.post("/generate-message-and-update-plan/")
# async def generate_message_and_update_plan(
#     background_tasks: BackgroundTasks,
#     trip_id: str = Body(...),
#     user_message: str = Body(...),
#     last_messages: str = Body(...)
# ):
async def generate_message_and_update_plan(
    req: Demo,
    background_tasks: BackgroundTasks
):
    bot_response = await chat_chain.arun(message=req.user_message)

    background_tasks.add_task(
        update_plan_in_background,
        trip_id=req.trip_id,
        user_message=req.user_message,
        last_messages=req.last_messages
    )
    return {
        "trip_id": req.trip_id,
        "bot_response": bot_response
    }

async def update_plan_in_background(trip_id: str, user_message: str, last_messages: str):
    plan_doc = await trips_information_col.find_one({"trip_id": ObjectId(trip_id)})
    if not plan_doc:
        return

    current_plan = plan_doc.get("data", {})
    # plan_json_text = await information_update_chain.arun(
    #     last_user_message=user_message,
    #     messages_history=last_messages,
    #     current_plan=json.dumps(current_plan)
    # )
    
    plan_json_text = await information_update_chain.arun(
    last_user_message=user_message,
    message_history=json.dumps(last_messages), 
    current_plan=json.dumps(current_plan)
)

    print("last user mess: ", user_message)
    print("last message: ", last_messages)

    try:
        start = plan_json_text.find("{")
        end = plan_json_text.rfind("}") + 1
        json_str = plan_json_text[start:end]
        new_plan = json.loads(json_str)
    except Exception as e:
        print(f"Plan JSON parsing failed: {str(e)}")
        return

    await trips_information_col.update_one(
        {"trip_id": ObjectId(trip_id)},
        {"$set": {"data": new_plan, "updated_at": datetime.utcnow()}}
    )

    print(f"✅ Background plan update done for trip_id: {trip_id}")
    print(new_plan)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("togetherai:app", host="127.0.0.1", port=8001, reload=True)


