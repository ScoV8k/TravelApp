from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_together import ChatTogether
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.output_parsers import StructuredOutputParser
from langchain.output_parsers import ResponseSchema

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
    ("system", "You are the travel planner assistant"), 
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{message}"),
    # ("system", f"Zwróć odpowiedź w czystym formacie JSON. {parser.get_format_instructions()}"),

])

chain = LLMChain(llm=llm, prompt=prompt_template2, memory=memory)

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
    wynik = await chain.arun(message=req.message)
    return {"message": req.message, "response": wynik}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("togetherai:app", host="127.0.0.1", port=8001, reload=True)

