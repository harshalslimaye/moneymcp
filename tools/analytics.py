from fastmcp import FastMCP

from db import get_db


def register(mcp: FastMCP):
    @mcp.tool()
    async def get_summary(
        start_date: str = "",
        end_date: str = "",
    ) -> dict:
        """Get total spending by category, with an optional date range (YYYY-MM-DD)."""
        query = "SELECT category, SUM(amount) as total, COUNT(*) as count FROM expenses WHERE 1=1"
        params: list = []

        if start_date:
            query += " AND expense_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND expense_date <= ?"
            params.append(end_date)

        query += " GROUP BY category ORDER BY total DESC"

        async with await get_db() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            by_category = [{"category": r["category"], "total": round(r["total"], 2), "count": r["count"]} for r in rows]
            grand_total = sum(r["total"] for r in by_category)
            return {"total": round(grand_total, 2), "by_category": by_category}

    @mcp.tool()
    async def list_categories() -> list[str]:
        """List all distinct expense categories."""
        async with await get_db() as db:
            cursor = await db.execute("SELECT DISTINCT category FROM expenses ORDER BY category")
            rows = await cursor.fetchall()
            return [r["category"] for r in rows]
