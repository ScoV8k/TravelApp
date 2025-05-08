from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

client = AsyncIOMotorClient(MONGO_URI)
db = client["TripLLM"]

users_col = db["users"]
trips_col = db["trips"]
messages_col = db["messages"]

async def insert_test_message():
    message = {
        "trip_id": "gruzja2025",
        "user_message": "Chcę pojechać do Batumi",
        "llm_response": "Świetnie! To piękne miasto nad Morzem Czarnym.",
        "timestamp": datetime.now()
    }
    result = await messages_col.insert_one(message)
    print("Wstawiono wiadomość z ID:", result.inserted_id)
