from langchain_core.prompts import ChatPromptTemplate


final_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are summarizing the result of a browser automation task.

Be concise.
Say what was completed.
If the task was not fully completed, say what blocked it.
Do not invent results.
""",
        ),
        (
            "human",
            """
GOAL:
{goal}

PLAN:
{plan}

RECENT MESSAGES:
{messages}

Write the final answer.
""",
        ),
    ]
)