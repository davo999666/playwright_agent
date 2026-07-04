# main.py

import asyncio

from graphs.browser_graph import BrowserGraph
from mcp_client.playwright_client import get_mcp_tools


async def main():
    goal = "Find an apartment to buy with a budget of $50,000."
    start_url = "https://www.list.am/en/"

    # Keep the browser alive for the whole run via the async context manager.
    async with get_mcp_tools() as mcp_tools:
        agent = BrowserGraph(mcp_tools)
        result = await agent.run(goal=goal, start_url=start_url)

    print("\n=========== RUN RESULT ===========")
    print("Final answer:")
    print(result.get("final_answer") or "(no answer produced)")
    print("Plan used:")
    print(result.get("plan"))
    print("Iterations:", result.get("iteration"))
    print("Replans:", result.get("replan_count"))
    print("==================================\n")


if __name__ == "__main__":
    asyncio.run(main())
