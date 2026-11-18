"""MCP connector: job postings dataset + application tracking store.

Run on its own with:  python connector/mcp_server.py
Any MCP client can launch it over stdio. The app's Market Analyst uses it too.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mcp.server.fastmcp import FastMCP  # noqa: E402

from app import db  # noqa: E402
from app.connector import search_postings_local  # noqa: E402
from app.governance import dataset_info  # noqa: E402
from app.tools import application_tracker  # noqa: E402

server = FastMCP("placement-readiness", log_level="ERROR")


@server.tool()
def search_postings(query: str = "", mode: str = "phrase", limit: int = 300) -> dict:
    """Search job postings by title. mode is phrase, tokens or all."""
    return search_postings_local(query, mode, limit)


@server.tool()
def get_posting(posting_id: int) -> dict:
    """Return one job posting, so a citation can be checked."""
    rows = db.query("SELECT * FROM postings WHERE id = ?", (posting_id,))
    return rows[0] if rows else {"error": "not found"}


@server.tool()
def get_dataset_info() -> dict:
    """Describe the dataset: size, dates, sources and its confidence cap."""
    return dataset_info()


@server.tool()
def list_applications() -> dict:
    """List the student's tracked applications."""
    return application_tracker("list")


@server.tool()
def add_application(company: str, role: str, job_description: str = "", status: str = "SAVED") -> dict:
    """Add a tracked application."""
    return application_tracker("add", company=company, role=role, job_description=job_description, status=status)


@server.tool()
def update_application(application_id: int, status: str = "", notes: str = "", follow_up_on: str = "") -> dict:
    """Update a tracked application's status, notes or follow-up date."""
    fields = {k: v for k, v in {"status": status, "notes": notes, "follow_up_on": follow_up_on}.items() if v}
    return application_tracker("update", application_id, **fields)


if __name__ == "__main__":
    db.init_db()
    server.run("stdio")
