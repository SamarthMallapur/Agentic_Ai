"""Client side of the MCP connector, with a direct fallback."""
import asyncio
import json
import logging
import os
import re
import sys

from . import config, db
from .governance import dataset_info
from .tools import application_tracker

# Windows logs a harmless pipe-reset error each time an MCP subprocess closes.
logging.getLogger("asyncio").setLevel(logging.CRITICAL)

GENERIC_TITLE_WORDS = {"engineer", "developer", "software", "senior", "junior", "intern", "associate", "trainee", "analyst"}


def search_postings_local(query: str = "", mode: str = "phrase", limit: int = 300) -> dict:
    limit = max(1, min(int(limit), 1000))
    columns = "id, title, company, location, description, skills, posted_on, source, source_row"
    where, params = "", ()
    if mode == "phrase" and query.strip():
        where, params = "WHERE title LIKE ?", (f"%{query.strip()}%",)
    elif mode == "tokens":
        words = re.findall(r"[a-z]+", query.lower())
        tokens = [t for t in words if len(t) > 2 and t not in GENERIC_TITLE_WORDS] or [t for t in words if len(t) > 2]
        if tokens:
            where = "WHERE " + " OR ".join("title LIKE ?" for _ in tokens)
            params = tuple(f"%{t}%" for t in tokens)
    rows = db.query(f"SELECT {columns} FROM postings {where} ORDER BY posted_on DESC, id LIMIT ?", (*params, limit))
    return {"query": query, "mode": mode, "count": len(rows), "postings": rows}


class DirectConnector:
    """Same interface as MCP, used for fast page loads and as the fallback."""

    transport = "direct"

    def call(self, tool: str, **args) -> dict:
        if tool == "search_postings":
            return search_postings_local(**args)
        if tool == "get_dataset_info":
            return dataset_info()
        if tool == "list_applications":
            return application_tracker("list")
        raise ValueError(f"Unknown tool: {tool}")


class MCPConnector:
    """Calls the real MCP server over stdio. Falls back and records it if that fails."""

    def __init__(self):
        self.transport = "mcp-stdio"
        self.calls: list[str] = []

    async def _call(self, tool: str, args: dict) -> dict:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        params = StdioServerParameters(
            command=sys.executable, args=[str(config.MCP_SERVER)], env=dict(os.environ), cwd=str(config.ROOT)
        )
        with open(os.devnull, "w") as quiet:
            async with stdio_client(params, errlog=quiet) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool, args)
        if result.isError:
            raise RuntimeError(result.content[0].text)
        return json.loads(result.content[0].text)

    def call(self, tool: str, **args) -> dict:
        self.calls.append(tool)
        if self.transport == "mcp-stdio":
            try:
                return asyncio.run(asyncio.wait_for(self._call(tool, args), timeout=30))
            except Exception:
                self.transport = "direct (MCP failed)"
        return DirectConnector().call(tool, **args)
