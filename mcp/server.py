import asyncio
import json
import os
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from memory.profile_memory import ProfileMemory
from memory.session_memory import SessionMemory
from memory.feedback_memory import FeedbackMemory
from tools.application_tracker import ApplicationTracker
from tools.market_analysis import MarketAnalysis

app = Server("placement-mcp-server")

profile_db = ProfileMemory()
session_db = SessionMemory()
feedback_db = FeedbackMemory()
app_tracker = ApplicationTracker()
market_db = MarketAnalysis()

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(name="get_student_profile", description="Get the long-term student profile.", inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="update_student_profile", description="Update the student profile.", inputSchema={"type": "object", "properties": {"profile_data": {"type": "object"}}}),
        types.Tool(name="get_market_statistics", description="Get job market statistics.", inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="get_application_history", description="Get job application history.", inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="add_application", description="Add a new job application.", inputSchema={"type": "object", "properties": {"app_data": {"type": "object"}}}),
        types.Tool(name="get_feedback_memory", description="Get all previous feedback.", inputSchema={"type": "object", "properties": {}}),
        types.Tool(name="save_feedback", description="Save feedback recommendation.", inputSchema={"type": "object", "properties": {"suggestion": {"type": "string"}, "status": {"type": "string"}, "reason": {"type": "string"}, "context": {"type": "string"}}})
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_student_profile":
        data = profile_db.get_profile()
        return [types.TextContent(type="text", text=json.dumps(data))]
    elif name == "update_student_profile":
        profile_db.update_profile(arguments["profile_data"])
        return [types.TextContent(type="text", text=json.dumps({"status": "success"}))]
    elif name == "get_market_statistics":
        data = market_db.get_market_statistics()
        return [types.TextContent(type="text", text=json.dumps(data))]
    elif name == "get_application_history":
        data = app_tracker.get_applications()
        return [types.TextContent(type="text", text=json.dumps(data))]
    elif name == "add_application":
        app_id = app_tracker.add_application(arguments["app_data"])
        return [types.TextContent(type="text", text=json.dumps({"status": "success", "id": app_id}))]
    elif name == "get_feedback_memory":
        data = feedback_db.get_all_feedback()
        return [types.TextContent(type="text", text=json.dumps(data))]
    elif name == "save_feedback":
        feedback_db.add_feedback(arguments["suggestion"], arguments["status"], arguments["reason"], arguments["context"])
        return [types.TextContent(type="text", text=json.dumps({"status": "success"}))]
    
    raise ValueError(f"Unknown tool: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
