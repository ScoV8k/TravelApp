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
plans_col = db["plans"]
trips_information_col = db["trips-information"]
