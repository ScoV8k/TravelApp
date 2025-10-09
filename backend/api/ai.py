from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
from bson import ObjectId
import json
import asyncio

from core.database import plans_col, trips_col, users_col, trips_information_col
from travelplan.traveljson import get_empty_plan2
from chains.chat_chain import chat_chain
from chains.plan_generator_chain import plan_generator_chain, json2_skeleton
from chains.information_update_chain import information_update_chain
from enrich import enrich_plan_with_locations
from api.models import PlanDB

router = APIRouter()

# MODELE REQUESTÓW
class Demo(BaseModel):
    trip_id: str
    user_message: str
    last_messages: List[Dict]

async def try_parse_json(response_text: str, retries: int = 2):
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

@router.post("/generate-plan/{trip_id}", response_model=PlanDB)
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
        except Exception as e:
            print(f"⚠️ Could not fetch user info: {e}")

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
- Attractions MUST be CONCRETE places (e.g. "Louvre Museum", "Central Park", "Restaurant XYZ") and NOT generic activities (like "walk around the city" or "eat dinner").


TRAVEL INFORMATION:
{json.dumps(travel_information, indent=2)}

INFORMATION FROM USER:
{user_about_info}

JSON:
{json2_skeleton}
"""

    response = await plan_generator_chain.llm.ainvoke(raw_prompt)
    response_text = response.content
    print(f"🟢 Raw model response:\n{response_text}\n")

    plan_data = await try_parse_json(response_text, retries=2)
    enriched_plan = await enrich_plan_with_locations(plan_data)

    plan_doc = {
        "trip_id": ObjectId(trip_id),
        "data": enriched_plan,
        "updated_at": datetime.utcnow()
    }

    await plans_col.replace_one({"trip_id": ObjectId(trip_id)}, plan_doc, upsert=True)
    await trips_col.update_one({"_id": ObjectId(trip_id)}, {"$set": {"status": "planned"}})

    new_plan = await plans_col.find_one({"trip_id": ObjectId(trip_id)})
    if not new_plan:
        raise HTTPException(status_code=500, detail="Failed to store generated plan")

    new_plan["_id"] = str(new_plan["_id"])
    new_plan["trip_id"] = str(new_plan["trip_id"])

    return new_plan

@router.post("/generate-message-and-update-information/")
async def generate_message_and_update_plan(req: Demo, background_tasks: BackgroundTasks):
    plan_doc = await trips_information_col.find_one({"trip_id": ObjectId(req.trip_id)})

    res = await chat_chain.ainvoke({"input": req.user_message, "trip_gathered_information": plan_doc})
    bot_response_text = res["output"]

    booking_link = None
    price = None
    departure_outbound_from = None
    departure_outbound_date = None
    departure_inbound_from = None
    departure_inbound_date = None
    if "intermediate_steps" in res:
        for action, observation in res["intermediate_steps"]:
            if action.tool == "flight_searcher":
                try:
                    flight_data = json.loads(observation)
                    if isinstance(flight_data, list) and len(flight_data) > 0:
                        booking_link = flight_data[0].get("booking_link")
                        price = flight_data[0].get("price")
                        departure_outbound_from = flight_data[0].get("outbound_flight").get("departure_from")
                        departure_outbound_date = flight_data[0].get("outbound_flight").get("departure_time")
                        departure_inbound_from = flight_data[0].get("inbound_flight").get("departure_from")
                        departure_inbound_date = flight_data[0].get("inbound_flight").get("departure_time")
                        break
                except (json.JSONDecodeError, IndexError, KeyError) as e:
                    print(f"⚠️ Could not extract booking link from tool observation: {e}")

    background_tasks.add_task(update_plan_in_background, req.trip_id, req.user_message, req.last_messages, plan_doc)

    return {
        "trip_id": req.trip_id,
        "bot_response": {
            "text": bot_response_text,
            "link": booking_link,
            "flight": {
                "link": booking_link,
                "price": price,
                "departure_outbound_from": departure_outbound_from,
                "departure_outbound_time": departure_outbound_date,
                "departure_inbound_from": departure_inbound_from,
                "departure_inbound_time": departure_inbound_date
            }
        }
    }

async def update_plan_in_background(trip_id: str, user_message: str, last_messages: List[Dict], plan_doc: dict):
    current_plan = plan_doc.get("data", {})
    plan_json_text = await information_update_chain.arun(
        last_user_message=user_message,
        message_history=json.dumps(last_messages),
        current_plan=json.dumps(current_plan)
    )

    try:
        start = plan_json_text.find("{")
        end = plan_json_text.rfind("}") + 1
        new_plan = json.loads(plan_json_text[start:end])
    except Exception as e:
        print(f"Plan JSON parsing failed: {str(e)}")
        return

    await trips_information_col.update_one(
        {"trip_id": ObjectId(trip_id)},
        {"$set": {"data": new_plan, "updated_at": datetime.utcnow()}}
    )

    print(f"✅ Background plan update done for trip_id: {trip_id}")
    print(new_plan)
