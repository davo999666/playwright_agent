# test_mcp_tools.py

import asyncio

from mcp_client.playwright_client import get_mcp_tools
from tools.tool_registry import init_tools, get_tools_names


async def main():
    async with get_mcp_tools() as tools:
        init_tools(tools)

        print(get_tools_names())


if __name__ == "__main__":
    asyncio.run(main())