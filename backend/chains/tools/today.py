from langchain.tools import StructuredTool
from datetime import datetime

def get_today() -> str:
    return datetime.today().strftime("%A, %d %B %Y")

today_tool = StructuredTool.from_function(
    name="get_today_date",
    description="Returns today's date. Use this when the user asks about the current date or when you need to refer to 'today'.",
    func=get_today
)