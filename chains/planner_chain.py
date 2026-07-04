from langchain_core.output_parsers import JsonOutputParser, StrOutputParser

from llm.model import model
from prompts.planner_prompt import planner_prompt
from prompts.final_prompt import final_prompt


planner_chain = planner_prompt | model | JsonOutputParser()
final_chain = final_prompt | model | StrOutputParser()