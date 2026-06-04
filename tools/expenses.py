from datetime import date, datetime
from typing import Optional

from fastmcp import FastMCP

from db import get_db


def register(mcp: FastMCP):
    @mcp.tool()
    async def add_expense(
        amount: float,
        category: str,
        description: str = "",
        expense_date: str = "",
    ) -> dict:
        """Add a new expense. expense_date should be YYYY-MM-DD; defaults to today."""
        if amount <= 0:
            return {"error": "Amount must be positive"}
        if not expense_date:
            expense_date = date.today().isoformat()
        else:
            try:
                date.fromisoformat(expense_date)
            except ValueError:
                return {"error": "expense_date must be in YYYY-MM-DD format"}

        async with await get_db() as db:
            cursor = await db.execute(
                "INSERT INTO expenses (amount, category, description, expense_date, created_at) VALUES (?, ?, ?, ?, ?)",
                (amount, category.strip().lower(), description.strip(), expense_date, datetime.now().isoformat()),
            )
            await db.commit()
            return {"id": cursor.lastrowid, "amount": amount, "category": category, "date": expense_date}

    @mcp.tool()
    async def list_expenses(
        category: str = "",
        start_date: str = "",
        end_date: str = "",
        limit: int = 50,
    ) -> list[dict]:
        """List expenses, optionally filtered by category and/or date range (YYYY-MM-DD)."""
        query = "SELECT * FROM expenses WHERE 1=1"
        params: list = []

        if category:
            query += " AND category = ?"
            params.append(category.strip().lower())
        if start_date:
            query += " AND expense_date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND expense_date <= ?"
            params.append(end_date)

        query += " ORDER BY expense_date DESC LIMIT ?"
        params.append(limit)

        async with await get_db() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    @mcp.tool()
    async def delete_expense(expense_id: int) -> dict:
        """Delete an expense by ID."""
        async with await get_db() as db:
            cursor = await db.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            await db.commit()
            if cursor.rowcount == 0:
                return {"error": f"No expense found with id {expense_id}"}
            return {"deleted": expense_id}

    @mcp.tool()
    async def update_expense(
        expense_id: int,
        amount: Optional[float] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        expense_date: Optional[str] = None,
    ) -> dict:
        """Update one or more fields of an existing expense."""
        updates = []
        params = []

        if amount is not None:
            if amount <= 0:
                return {"error": "Amount must be positive"}
            updates.append("amount = ?")
            params.append(amount)
        if category is not None:
            updates.append("category = ?")
            params.append(category.strip().lower())
        if description is not None:
            updates.append("description = ?")
            params.append(description.strip())
        if expense_date is not None:
            try:
                date.fromisoformat(expense_date)
            except ValueError:
                return {"error": "expense_date must be in YYYY-MM-DD format"}
            updates.append("expense_date = ?")
            params.append(expense_date)

        if not updates:
            return {"error": "No fields to update"}

        params.append(expense_id)
        async with await get_db() as db:
            cursor = await db.execute(
                f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?", params
            )
            await db.commit()
            if cursor.rowcount == 0:
                return {"error": f"No expense found with id {expense_id}"}
            row = await (await db.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))).fetchone()
            return dict(row)
