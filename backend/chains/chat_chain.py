# # from langchain_together import ChatTogether
# # from langchain.chains import LLMChain
# from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.memory import ConversationBufferMemory

# # chat_llm = ChatTogether(
# #     model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
# #     temperature=0.7,
# #     max_tokens=512
# # )

# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# chat_llm_prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a friendly travel assistant. Your task is to help the user plan a trip by asking one question at a time. Ask specific, small questions to gradually gather details. Do NOT propose or generate a full trip plan. Only ask questions like: 'Where do you want to go?', 'What dates are you planning?', 'What kind of places do you like?', 'What’s your budget?', etc."),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "{message}"),
# ])

# # chat_chain = LLMChain(llm=chat_llm, prompt=chat_llm_prompt, memory=memory)

from dotenv import load_dotenv
from datetime import datetime, date, timedelta
from dateutil.parser import parse as parse_date

from langchain_together import ChatTogether
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool, StructuredTool

from langchain.agents import create_react_agent

from chains.tools.weather import current_weather_tool, forecast_weather_tool
from chains.tools.flights import flight_searcher_tool
from chains.tools.today import today_tool

load_dotenv()

tools = [current_weather_tool, forecast_weather_tool, flight_searcher_tool, today_tool]

chat_llm = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0.2,
    max_tokens=2048
)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)


template = """
You are a friendly travel assistant. Your task is to help the user plan a trip by asking one question at a time. Ask specific, small questions to gradually gather details. Do NOT propose or generate a full trip plan. Only ask questions like: 'Where do you want to go?', 'What dates are you planning?', 'What kind of places do you like?', 'What’s your budget?', etc.

When you need to find specific, real-time information like weather, use the available tools.

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:


Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action


When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:


Thought: Do I need to use a tool? No
Final Answer: [your response here]


Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
"""



prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "chat_history", "agent_scratchpad"],
    template=template
)

agent = create_react_agent(
    llm=chat_llm,
    tools=tools,
    prompt=prompt
)

chat_chain = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)



# print(search_flights("francja"))