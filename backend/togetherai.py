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

from core.database import trips_information_col

from travelplan.traveljson import get_empty_plan2


from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.7,
    max_tokens=512
)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

prompt_template2 = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly travel assistant. Your task is to help the user plan a trip by asking one question at a time. Ask specific, small questions to gradually gather details. Do NOT propose or generate a full trip plan. Only ask questions like: 'Where do you want to go?', 'What dates are you planning?', 'What kind of places do you like?', 'What’s your budget?', etc."), 
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{message}"),

])

conversation_chain = LLMChain(llm=llm, prompt=prompt_template2, memory=memory)



# PLAN MODEL — bez pamięci

llm_plan = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.7,
    max_tokens=512
)

prompt_plan = PromptTemplate( #prompt po angielsku
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

json2_skeleton = get_empty_plan2()
# """
# {
#   "trip_name": null,
#   "start_date": null,
#   "end_date": null,
#   "duration_days": null,
#   "destination_country": null,
#   "destination_cities": [],
#   "daily_plan": [
#     {
#       "day": null,
#       "date": null,
#       "city": null,
#       "summary": null,
#       "accommodation": {
#         "hotel_name": null,
#         "check_in": null,
#         "address": null
#       },
#       "activities": [
#         {
#           "time": null,
#           "title": null,
#           "description": null,
#           "location": {
#             "name": null,
#             "lat": null,
#             "lng": null
#           },
#           "type": null,
#           "map_link": null
#         }
#       ],
#       "notes": null
#     }
#   ],
#   "map_summary": {
#     "locations": [
#       {
#         "name": null,
#         "lat": null,
#         "lng": null,
#         "day": null,
#         "type": null
#       }
#     ]
#   },
#   "general_notes": []
# }
# """


# GENEROWANIE GOTOWEGO PLANU
llm_plan_generator = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    # model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.7,
    max_tokens=4096
)

prompt_plan_generate = PromptTemplate( #prompt po angielsku
    input_variables=["current_plan"],
    template="""
Wygeneruj mi bogaty plan podrózy na podstawie informacji zawartych w wypełnionym JSON 1. I zwróć cały plan w formacie JSON 2. Jeśli n

JSON 1:
{current_plan}
JSON 2:
""" + json2_skeleton
) 


plan_generator_chain = LLMChain(llm=llm_plan_generator, prompt=prompt_plan_generate)


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
    plan_doc = await trips_information_col.find_one({"trip_id": ObjectId(req.trip_id)})
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

    await trips_information_col.update_one(
        {"trip_id": ObjectId(req.trip_id)},
        {"$set": {"data": plan_data, "updated_at": datetime.utcnow()}}
    )

    return {"trip_id": req.trip_id, "updated": True, "data": plan_data}


# @app.post("/generate-plan/{trip_id}")
# async def generate_plan(trip_id: str):

#     # ✅ Pobierz istniejący plan z bazy danych
#     plan_doc = await plans_col.find_one({"trip_id": ObjectId(trip_id)})
#     if not plan_doc:
#         raise HTTPException(status_code=404, detail="Plan not found for this trip_id")

#     current_plan = plan_doc.get("data", {})
#     print(current_plan)

#     # ✅ Przekaż plan i wiadomość do modelu aktualizującego
#     plan_json_text = await plan_generator_chain.arun(
#         current_plan=json.dumps(current_plan)
#     )

#     print(f"🟢 Surowa odpowiedź LLM:\n{plan_json_text}\n")

#     try:
#         start = plan_json_text.find("{")
#         end = plan_json_text.rfind("}") + 1
#         json_str = plan_json_text[start:end]
#         print(f"🔵 Próba parsowania JSON:\n{json_str}\n")
#         plan_data = json.loads(json_str)
#     except Exception:
#         raise HTTPException(status_code=500, detail="Model nie zwrócił poprawnego JSON-a")

#     return plan_data


# import re
# import asyncio

# def fix_broken_json(text: str) -> str:
#     # usuń komentarze i nadmiarowe przecinki
#     cleaned = re.sub(r",\s*}", "}", text)
#     cleaned = re.sub(r",\s*]", "]", cleaned)
#     cleaned = re.sub(r"//.*", "", cleaned)
#     return cleaned

# async def try_parse_json(response_text: str, retries: int = 1):
#     for attempt in range(retries + 1):
#         try:
#             start = response_text.find("{")
#             end = response_text.rfind("}") + 1
#             json_str = response_text[start:end]
#             json_str = fix_broken_json(json_str)
#             return json.loads(json_str)
#         except Exception as e:
#             if attempt == retries:
#                 raise HTTPException(status_code=500, detail=f"Błąd JSON-a: {str(e)}")
#             await asyncio.sleep(1)

import re
import asyncio
import json
from fastapi import HTTPException

def clean_control_chars(text: str) -> str:
    """Usuń niedozwolone znaki kontrolne z JSON-a (np. ASCII < 32 z wyjątkiem \n i \t)"""
    return ''.join(ch if ch in ('\n', '\t') or ord(ch) >= 32 else ' ' for ch in text)

def fix_broken_json(text: str) -> str:
    """Usuń najczęstsze błędy formatowania JSON-a"""
    cleaned = re.sub(r",\s*}", "}", text)   # przecinki przed }
    cleaned = re.sub(r",\s*]", "]", cleaned)  # przecinki przed ]
    cleaned = re.sub(r"//.*", "", cleaned)   # JS-style comments
    cleaned = clean_control_chars(cleaned)   # znaki kontrolne
    return cleaned

async def try_parse_json(response_text: str, retries: int = 2):
    """Spróbuj sparsować JSON z poprawkami i retry"""
    for attempt in range(retries + 1):
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
            # json_str = fix_broken_json(json_str)
            return json.loads(json_str)
        except Exception as e:
            print(f"🔴 Błąd przy parsowaniu JSON (podejście {attempt+1}): {str(e)}")
            if attempt == retries:
                raise HTTPException(status_code=500, detail=f"Błąd JSON-a: {str(e)}")
            await asyncio.sleep(1)


# @app.post("/generate-plan/{trip_id}")
# async def generate_plan(trip_id: str):
#     # Pobierz plan z Mongo
#     plan_doc = await plans_col.find_one({"trip_id": ObjectId(trip_id)})
#     if not plan_doc:
#         raise HTTPException(status_code=404, detail="Plan not found")

#     current_plan = plan_doc.get("data", {})

#     # Sformatuj prompt ręcznie
#     raw_prompt = f"""
# Wygeneruj bogaty i szczegółowy plan podróży na podstawie danych z JSON 1. 
# Wypełnij plan w formacie JSON 2. Jeśli brakuje danych – dodaj własne ciekawe propozycje atrakcji. 

# 🔴 BARDZO WAŻNE:
# - ZWRÓĆ TYLKO POPRAWNY I CZYSTY JSON – BEZ KOMENTARZY, BEZ TEKSTU PRZED ANI PO.
# - JSON musi być poprawny składniowo (parsowalny funkcją json.loads w Pythonie).
# - Upewnij się, że KAŻDY element listy lub obiektu jest ODDZIELONY przecinkiem (`,`).
# - NIE używaj przecinka po ostatnim elemencie listy lub obiektu.

# JSON 1:
# {json.dumps(current_plan, indent=2)}

# JSON 2:
# {json2_skeleton}
# """



#     # Zapytaj model
#     response = await llm_plan_generator.ainvoke(raw_prompt)
#     response_text = response.content  # <- poprawka

#     print(f"🟢 Odpowiedź LLM:\n{response_text}\n")

#     # Wyciągnij JSON
#     # try:
#     #     start = response_text.find("{")
#     #     end = response_text.rfind("}") + 1
#     #     json_str = response_text[start:end]
#     #     print(f"🔵 Parsowany JSON:\n{json_str}")
#     #     plan_data = json.loads(json_str)
#     # except Exception as e:
#     #     raise HTTPException(status_code=500, detail=f"Błąd JSON-a: {str(e)}")
    
#     plan_data = await try_parse_json(response_text, retries=1)
#     return plan_data


@app.post("/generate-plan/{trip_id}")
async def generate_plan(trip_id: str):
    # Pobierz plan z Mongo
    plan_doc = await trips_information_col.find_one({"trip_id": ObjectId(trip_id)})
    if not plan_doc:
        raise HTTPException(status_code=404, detail="Plan not found")

    current_plan = plan_doc.get("data", {})

    # Sformatuj prompt ręcznie
    raw_prompt = f"""
Wygeneruj krótki plan podróży na podstawie danych z JSON 1. 
Wypełnij plan w formacie JSON 2. Jeśli brakuje danych – dodaj własne ciekawe propozycje atrakcji. 

🔴 BARDZO WAŻNE:
- ZWRÓĆ TYLKO POPRAWNY I CZYSTY JSON – BEZ KOMENTARZY, BEZ TEKSTU PRZED ANI PO.
- JSON musi być poprawny składniowo (parsowalny funkcją json.loads w Pythonie).
- Upewnij się, że KAŻDY element listy lub obiektu jest ODDZIELONY przecinkiem (`,`).
- NIE używaj przecinka po ostatnim elemencie listy lub obiektu.
- ZNAKI NOWEJ LINII w stringach powinny być zapisane jako \\n (podwójny backslash).

JSON 1:
{json.dumps(current_plan, indent=2)}

JSON 2:
{json2_skeleton}
"""

    # Zapytaj model
    response = await llm_plan_generator.ainvoke(raw_prompt)
    response_text = response.content

    print(f"🟢 Surowa odpowiedź modelu:\n{response_text}\n")

    # Spróbuj sparsować z poprawkami i retry
    plan_data = await try_parse_json(response_text, retries=2)

    return plan_data


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("togetherai:app", host="127.0.0.1", port=8001, reload=True)




