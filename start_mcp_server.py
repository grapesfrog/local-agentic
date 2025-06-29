#!/usr/bin/env python3
"""Script to start the MCP server on port 8002."""

import os
import sys
import asyncio

# Set the port before importing
os.environ['MCP_SERVER_PORT'] = '8002'

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.task_mcp_server import TaskMCPServer

async def main():
    """Start the MCP server on port 8002."""
    server = TaskMCPServer(host="localhost", port=8002)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main()) 