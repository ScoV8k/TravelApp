from fastapi import FastAPI
import api.users as users
import api.trips as trips
import api.messages as messages
import api.auth as auth
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Travel Planner App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(trips.router)
app.include_router(messages.router)
app.include_router(auth.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)