from langchain_together import ChatTogether
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

information_llm = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.7,
    max_tokens=512
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
