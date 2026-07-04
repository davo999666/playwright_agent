# main.py

import asyncio

from graphs.browser_graph import BrowserGraph
from mcp_client.playwright_client import get_mcp_tools


async def main():
    goal = """
            take screen shot and explain the content of the page.
            """

    start_url = "https://www.list.am/en/"

    # Use context manager to keep the browser alive for the entire application
    async with get_mcp_tools() as mcp_tools:
        agent = BrowserGraph(mcp_tools)
        await agent.run(goal=goal, start_url=start_url)


if __name__ == "__main__":
    asyncio.run(main())