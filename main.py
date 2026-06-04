import asyncio

from fastmcp import FastMCP

from db import init_db
from tools import expenses, analytics

mcp = FastMCP("moneymcp")

expenses.register(mcp)
analytics.register(mcp)

if __name__ == "__main__":
    asyncio.run(init_db())
    mcp.run()
