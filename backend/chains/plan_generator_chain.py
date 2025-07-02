from langchain_together import ChatTogether
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from travelplan.traveljson import get_empty_plan2

plan_generator_llm = ChatTogether(
    model="deepseek-ai/DeepSeek-V3",
    temperature=0.7,
    max_tokens=4096
)

json2_skeleton = get_empty_plan2()

plan_generator_llm_prompt = PromptTemplate(
    input_variables=["travel_information", "json2_skeleton"],
    template="""[...]"""
)

plan_generator_chain = LLMChain(llm=plan_generator_llm, prompt=plan_generator_llm_prompt)
