import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from mcp import StdioServerParameters

MCP_SERVER_PATH = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp", "server.py")
)

placement_mcp_toolset = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[MCP_SERVER_PATH],
        )
    )
)

intake_agent = Agent(
    name="intake_agent",
    model="gemini-3.8-flash",
    description="Analyzes the user's intent and ensures all required context is available.",
    instruction="""
    You are the Intake Agent. The user wants help with placement preparation.
    1. Identify their goal (e.g., 'resume review', 'mock interview', 'market trends').
    2. Check if you have the necessary context. 
       - For resume review: need resume and Job Description.
       - For mock interview: need profile, resume, JD, and skill gaps.
       - For market trends: need profile.
    3. Use 'get_student_profile' MCP tool to fetch their profile.
    4. If critical information is missing, clearly ask the user for it.
    5. Output the structured intent and any missing data.
    """,
    tools=[placement_mcp_toolset],
    output_key="intake_state"
)

market_analyst = Agent(
    name="market_analyst",
    model="gemini-3.8-flash",
    description="Analyzes job market data and compares it against student profile.",
    instruction="""
    You are the Market Analyst.
    1. Use 'get_market_statistics' MCP tool to fetch current job market demand (skills, roles).
    2. Use 'get_student_profile' MCP tool to fetch the student's skills.
    3. Compare the market demand with the student's profile.
    4. Identify skill gaps (e.g., Market wants Python 74%, Student has it: YES/NO).
    5. Output a structured summary of market trends and the student's personal skill gaps.
    """,
    tools=[placement_mcp_toolset],
    output_key="market_analysis"
)

# ... Other agents will be defined here or imported.
