# test_mcp_tools.py

import asyncio

from mcp_client.playwright_client import get_mcp_tools




async def main():
    async with get_mcp_tools() as tools:
        print("TOOLS COUNT:", len(tools))
        print("=" * 80)

        for tool in tools:
            print("NAME:", tool.name)
            print("TYPE:", type(tool))
            print("DESCRIPTION:", tool.description)
            print("ARGS:")
            print(tool.args)

            print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())