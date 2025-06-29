"""MCP server implementation for task management tools."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import asyncio
from aiohttp import web, ClientSession
from typing import Dict, Any, List
import logging
from data_store.task_store import TaskStore
from mcp_server.tools import TaskTools
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TaskMCPServer:
    """Simple HTTP-based MCP server for task management tools."""

    def __init__(self, host: str = "localhost", port: int = 8002):
        """Initialize the MCP server."""
        self.host = host
        self.port = port
        self.task_store = TaskStore()
        self.task_tools = TaskTools(self.task_store)
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self) -> None:
        """Setup the HTTP routes for the MCP server."""
        self.app.router.add_post("/tools/add_task", self.handle_add_task)
        self.app.router.add_get("/tools/list_tasks", self.handle_list_tasks)
        self.app.router.add_post("/tools/mark_task_complete", self.handle_mark_task_complete)
        self.app.router.add_post("/tools/delete_task", self.handle_delete_task)
        self.app.router.add_post("/tools/clear_all_tasks", self.handle_clear_all_tasks)
        self.app.router.add_get("/tools/get_task_count", self.handle_get_task_count)
        self.app.router.add_get("/tools/get_task/{task_id}", self.handle_get_task)
        self.app.router.add_get("/health", self.handle_health)
        self.app.router.add_get("/tools", self.handle_list_tools)

    async def handle_add_task(self, request: web.Request) -> web.Response:
        """Handle add task requests."""
        try:
            data = await request.json()
            description = data.get("description", "")
            
            if not description:
                return web.json_response(
                    {"success": False, "error": "Description is required"},
                    status=400
                )
            
            result = self.task_tools.add_task(description)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error handling add task: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )

    async def handle_list_tasks(self, request: web.Request) -> web.Response:
        """Handle list tasks requests."""
        try:
            result = self.task_tools.list_tasks()
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error handling list tasks: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )

    async def handle_mark_task_complete(self, request: web.Request) -> web.Response:
        """Handle mark task complete requests."""
        try:
            data = await request.json()
            task_id = data.get("task_id", "")
            
            if not task_id:
                return web.json_response(
                    {"success": False, "error": "Task ID is required"},
                    status=400
                )
            
            result = self.task_tools.mark_task_complete(task_id)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error handling mark task complete: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )

    async def handle_delete_task(self, request: web.Request) -> web.Response:
        """Handle delete task requests."""
        try:
            data = await request.json()
            task_id = data.get("task_id", "")
            
            if not task_id:
                return web.json_response(
                    {"success": False, "error": "Task ID is required"},
                    status=400
                )
            
            result = self.task_tools.delete_task(task_id)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error handling delete task: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )

    async def handle_clear_all_tasks(self, request: web.Request) -> web.Response:
        """Handle clear all tasks requests."""
        try:
            result = self.task_tools.clear_all_tasks()
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error handling clear all tasks: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )

    async def handle_get_task_count(self, request: web.Request) -> web.Response:
        """Handle get task count requests."""
        try:
            result = self.task_tools.get_task_count()
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error handling get task count: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )

    async def handle_get_task(self, request: web.Request) -> web.Response:
        """Handle get task requests."""
        try:
            task_id = request.match_info["task_id"]
            result = self.task_tools.get_task(task_id)
            return web.json_response(result)
        except Exception as e:
            logger.error(f"Error handling get task: {e}")
            return web.json_response(
                {"success": False, "error": str(e)},
                status=500
            )

    async def handle_health(self, request: web.Request) -> web.Response:
        """Handle health check requests."""
        return web.json_response({
            "status": "healthy",
            "service": "Task MCP Server",
            "version": "1.0.0"
        })

    async def handle_list_tools(self, request: web.Request) -> web.Response:
        """Handle list tools requests."""
        tools = [
            {
                "name": "add_task",
                "description": "Add a new task",
                "parameters": {
                    "description": {"type": "string", "required": True}
                }
            },
            {
                "name": "list_tasks",
                "description": "List all tasks",
                "parameters": {}
            },
            {
                "name": "mark_task_complete",
                "description": "Mark a task as complete",
                "parameters": {
                    "task_id": {"type": "string", "required": True}
                }
            },
            {
                "name": "delete_task",
                "description": "Delete a task",
                "parameters": {
                    "task_id": {"type": "string", "required": True}
                }
            },
            {
                "name": "clear_all_tasks",
                "description": "Delete all tasks",
                "parameters": {}
            },
            {
                "name": "get_task_count",
                "description": "Get the total number of tasks",
                "parameters": {}
            },
            {
                "name": "get_task",
                "description": "Get a specific task by ID",
                "parameters": {
                    "task_id": {"type": "string", "required": True}
                }
            }
        ]
        
        return web.json_response({
            "tools": tools,
            "count": len(tools)
        })

    async def start(self) -> None:
        """Start the MCP server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"MCP Server started at http://{self.host}:{self.port}")
        
        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down MCP Server...")
        finally:
            await runner.cleanup()

    def run(self) -> None:
        """Run the MCP server."""
        asyncio.run(self.start())


async def main() -> None:
    """Main function to run the MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get configuration from environment
    host = os.getenv("MCP_SERVER_HOST", "localhost")
    port = int(os.getenv("MCP_SERVER_PORT", "8002"))
    
    # Create and start the server
    server = TaskMCPServer(host=host, port=port)
    await server.start()


if __name__ == "__main__":
    # For direct execution
    server = TaskMCPServer()
    server.run() 