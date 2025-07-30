from langchain_together import ChatTogether
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

information_llm = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0.8,
    max_tokens=2048
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
- Don't add or edit flights, but also don't delete it. Different system is doing it for you so don't mind this part of json.
- If you add travelers remember about adding one more called "You" (me, who is talking with you)
- YOU CAN'T ADD ACTIVITIES WITH NULL NAME!!!
- In additional notes add only important information about user preferences about the trip that you can't write in json (for example: User has allergy to penuts so cant go to penut restaurant)

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
