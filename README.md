# moneymcp

An MCP (Model Context Protocol) server for tracking personal expenses. Connect it to Claude or any MCP-compatible client to log, query, and analyze your spending through natural language.

## Features

- Add, update, and delete expenses
- Filter expenses by category and date range
- Summarize spending by category
- Persistent storage via SQLite

## Tools

| Tool | Description |
|------|-------------|
| `add_expense` | Add a new expense with amount, category, description, and date |
| `list_expenses` | List expenses, optionally filtered by category and/or date range |
| `update_expense` | Update one or more fields of an existing expense |
| `delete_expense` | Delete an expense by ID |
| `get_summary` | Get total spending grouped by category, with optional date range |
| `list_categories` | List all distinct expense categories |

## Setup

**Requirements:** Python 3.11+, [uv](https://github.com/astral-sh/uv)

```bash
# Install dependencies
uv sync

# Initialize the database
uv run python -c "import asyncio; from db import init_db; asyncio.run(init_db())"
```

## Running

```bash
uv run python main.py
```

## Connecting to Claude Desktop

Add the following to your Claude Desktop MCP config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "moneymcp": {
      "command": "uv",
      "args": ["run", "python", "main.py"],
      "cwd": "/path/to/moneymcp"
    }
  }
}
```

## Tech Stack

- [FastMCP](https://github.com/jlowin/fastmcp) — MCP server framework
- [aiosqlite](https://github.com/omnilib/aiosqlite) — async SQLite
