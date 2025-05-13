from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
# from langchain.output_parsers import StructuredOutputParser
# from langchain.output_parsers import ResponseSchema
from datetime import datetime
import os
from bson import ObjectId
import json

from core.database import plans_col


from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier",
    temperature=0.7,
    max_tokens=512
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt_template2 = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly travel assistant. Your task is to help the user plan a trip by asking one question at a time. Ask specific, small questions to gradually gather details. Do NOT propose or generate a full trip plan. Only ask questions like: 'Where do you want to go?', 'What dates are you planning?', 'What kind of places do you like?', 'What’s your budget?', etc."), 
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{message}"),
    # ("system", f"Zwróć odpowiedź w czystym formacie JSON. {parser.get_format_instructions()}"),

])

conversation_chain = LLMChain(llm=llm, prompt=prompt_template2, memory=memory)



# PLAN MODEL — bez pamięci
from langchain.chat_models import ChatOpenAI

llm_plan = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-classifier",
    temperature=0.7,
    max_tokens=512
)

prompt_plan = PromptTemplate(
    input_variables=["last_user_message", "current_plan"],
    template="""
Na podstawie ostatniej odpowiedzi użytkownika, zaktualizuj plan podróży w formacie JSON. Jako odpowiedź wygeneruj TYLKO sam JSON. Nie generuj wszystkiego od nowa, tylko zmodyfikuj istniejący plan tam, gdzie to konieczne. To znaczy jeśli jakieś pola są puste, zosta je puste, chyba ze uzytkownik podał jakieś dane.

Odpowiedź użytkownika:
{last_user_message}

Aktualny plan:
{current_plan}
"""
)


plan_update_chain = LLMChain(llm=llm_plan, prompt=prompt_plan)



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

@app.post("/generuj/")
async def generuj_opis(req: TematRequest):
    wynik = await conversation_chain.arun(message=req.message)
    return {"message": req.message, "response": wynik}

class PlanUpdateRequest(BaseModel):
    trip_id: str
    last_user_message: str
    bot_response: str

@app.post("/update-plan/")
async def update_plan(req: PlanUpdateRequest):
    print(f"🟡 Ostatnia wiadomość usera: {req.last_user_message}")
    print(f"🔵 Odpowiedź bota: {req.bot_response}")

    # ✅ Pobierz istniejący plan z bazy danych
    plan_doc = await plans_col.find_one({"trip_id": ObjectId(req.trip_id)})
    if not plan_doc:
        raise HTTPException(status_code=404, detail="Plan not found for this trip_id")

    current_plan = plan_doc.get("data", {})
    print(current_plan)

    # ✅ Przekaż plan i wiadomość do modelu aktualizującego
    plan_json_text = await plan_update_chain.arun(
        last_user_message=req.last_user_message,
        current_plan=json.dumps(current_plan)
    )

    print(f"🟢 Surowa odpowiedź LLM:\n{plan_json_text}\n")

    try:
        start = plan_json_text.find("{")
        end = plan_json_text.rfind("}") + 1
        json_str = plan_json_text[start:end]
        print(f"🔵 Próba parsowania JSON:\n{json_str}\n")
        plan_data = json.loads(json_str)
    except Exception:
        raise HTTPException(status_code=500, detail="Model nie zwrócił poprawnego JSON-a")

    print(f"🟣 Plan do zapisania w Mongo:\n{plan_data}")

    await plans_col.update_one(
        {"trip_id": ObjectId(req.trip_id)},
        {"$set": {"data": plan_data, "updated_at": datetime.utcnow()}}
    )

    return {"trip_id": req.trip_id, "updated": True, "data": plan_data}





if __name__ == "__main__":
    import uvicorn
    uvicorn.run("togetherai:app", host="127.0.0.1", port=8001, reload=True)




