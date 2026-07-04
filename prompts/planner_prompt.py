from langchain_core.prompts import ChatPromptTemplate


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a browser automation planner.

Create a short practical plan for the browser agent.

Rules:
- Use only information from the current page data.
- Each step should be one browser action.

Return strict JSON only.

Format:
{{
  "steps": [
    {{
      "id": 1,
      "action": {actions},
      "target": "real visible element or page",
      "input": "value or null",
      "reason": "why this step is needed"
    }}
  ],
  "steps": [
    {{
      "id": 2,
      "action": {actions},
      "target": "real visible element or page",
      "input": "value or null",
      "reason": "why this step is needed"
    }}
  ],
}}
""",
        ),
        (
            "human",
            """
GOAL:
{goal}

PAGE DATA:
{page_data}
""",
        ),
    ]
)