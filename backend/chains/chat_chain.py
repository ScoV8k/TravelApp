# from langchain_together import ChatTogether
# from langchain.chains import LLMChain
# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.memory import ConversationBufferMemory

# chat_llm = ChatTogether(
#     model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
#     temperature=0.7,
#     max_tokens=512
# )

# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# chat_llm_prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a friendly travel assistant. Your task is to help the user plan a trip by asking one question at a time. Ask specific, small questions to gradually gather details. Do NOT propose or generate a full trip plan. Only ask questions like: 'Where do you want to go?', 'What dates are you planning?', 'What kind of places do you like?', 'What’s your budget?', etc."),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "{message}"),
# ])

# chat_chain = LLMChain(llm=chat_llm, prompt=chat_llm_prompt, memory=memory)



import requests
from langchain_together import ChatTogether
from langchain.agents import initialize_agent, AgentType
from langchain.prompts import MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
import json
import os
from dotenv import load_dotenv


load_dotenv()

def get_real_weather(location: str) -> str:
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return json.dumps({"error": "Klucz API OpenWeatherMap nie został ustawiony w zmiennych środowiskowych."})
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()

        processed_data = {
            "location": data["name"],
            "temperature": f"{data['main']['temp']}°C",
            "feels_like": f"{data['main']['feels_like']}°C",
            "conditions": data['weather'][0]['description'],
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s"
        }
        
        return json.dumps(processed_data, ensure_ascii=False)

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return json.dumps({"error": f"City not found: {location}"})
        else:
            return json.dumps({"error": f"HTTP error occurred: {http_err}"})
    except Exception as e:
        return json.dumps({"error": f"An unexpected error occurred: {e}"})


weather_tool = Tool(
    name="real_weather_checker",
    description="Use this tool to check the current weather in a given city. Returns a JSON string with detailed weather information.",
    func=get_real_weather
)

# LLM
chat_llm = ChatTogether(
    # model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    model="deepseek-ai/DeepSeek-V3",
    temperature=0.7,
    max_tokens=512
)


memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

chat_chain = initialize_agent(
    tools=[weather_tool],
    llm=chat_llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors=True
)

