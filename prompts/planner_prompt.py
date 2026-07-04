from langchain_core.prompts import ChatPromptTemplate


planner_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are a Playwright MCP browser planner.

Create a short step-by-step browser plan.

Rules:
- Use ONLY elements from PAGE DATA.
- Use ONLY existing refs.
- Never invent refs.
- Each step = one browser action.
- Return JSON only.
- create several steps like 4.

Supported actions:
- browser_click
- browser_type
- browser_fill_form
- browser_snapshot
- browser_wait

JSON format:

{{
  "steps": [
    {{
      "id": 1,
      "action": "browser_click",
      "element": "visible element name",
      "ref": "element ref",
      "input": null,
      "reason": "why needed"
    }}
  ]
}}
"""
        ),
        (
            "human",
            """
GOAL:
{goal}

PAGE DATA:
{page_data}

Create the browser plan.
"""
        ),
    ]
)