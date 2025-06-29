"""A2A server implementation for inter-agent communication."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable
import aiohttp
from aiohttp import web
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class A2AServer:
    """A2A server for inter-agent communication."""

    def __init__(self, host: str = "localhost", port: int = 8001):
        """Initialize the A2A server."""
        self.host = host
        self.port = port
        self.app = web.Application()
        self.handlers: Dict[str, Callable] = {}
        self.setup_routes()

    def setup_routes(self) -> None:
        """Setup the HTTP routes for the A2A server."""
        self.app.router.add_post("/a2a/add_task", self.handle_a2a_add_task)
        self.app.router.add_get("/a2a/list_tasks", self.handle_a2a_list_tasks)
        self.app.router.add_post("/a2a/mark_task_complete", self.handle_a2a_mark_task_complete)
        self.app.router.add_post("/a2a/delete_task", self.handle_a2a_delete_task)
        self.app.router.add_get("/a2a/health", self.handle_a2a_health)
        self.app.router.add_get("/a2a/capabilities", self.handle_a2a_capabilities)

    def register_handler(self, method: str, handler: Callable) -> None:
        """Register a handler for a specific A2A method."""
        self.handlers[method] = handler
        logger.info(f"Registered A2A handler for method: {method}")

    async def handle_a2a_add_task(self, request: web.Request) -> web.Response:
        """Handle A2A add task requests."""
        try:
            data = await request.json()
            description = data.get("description", "")
            
            if not description:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Description is required",
                        "protocol": "A2A"
                    },
                    status=400
                )
            
            if "add_task" in self.handlers:
                result = await self.handlers["add_task"](description)
                return web.json_response({
                    "success": True,
                    "result": result,
                    "protocol": "A2A"
                })
            else:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Add task handler not registered",
                        "protocol": "A2A"
                    },
                    status=501
                )
        except Exception as e:
            logger.error(f"Error handling A2A add task: {e}")
            return web.json_response(
                {
                    "success": False,
                    "error": str(e),
                    "protocol": "A2A"
                },
                status=500
            )

    async def handle_a2a_list_tasks(self, request: web.Request) -> web.Response:
        """Handle A2A list tasks requests."""
        try:
            if "list_tasks" in self.handlers:
                result = await self.handlers["list_tasks"]()
                return web.json_response({
                    "success": True,
                    "result": result,
                    "protocol": "A2A"
                })
            else:
                return web.json_response(
                    {
                        "success": False,
                        "error": "List tasks handler not registered",
                        "protocol": "A2A"
                    },
                    status=501
                )
        except Exception as e:
            logger.error(f"Error handling A2A list tasks: {e}")
            return web.json_response(
                {
                    "success": False,
                    "error": str(e),
                    "protocol": "A2A"
                },
                status=500
            )

    async def handle_a2a_mark_task_complete(self, request: web.Request) -> web.Response:
        """Handle A2A mark task complete requests."""
        try:
            data = await request.json()
            task_id = data.get("task_id", "")
            
            if not task_id:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Task ID is required",
                        "protocol": "A2A"
                    },
                    status=400
                )
            
            if "mark_task_complete" in self.handlers:
                result = await self.handlers["mark_task_complete"](task_id)
                return web.json_response({
                    "success": True,
                    "result": result,
                    "protocol": "A2A"
                })
            else:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Mark task complete handler not registered",
                        "protocol": "A2A"
                    },
                    status=501
                )
        except Exception as e:
            logger.error(f"Error handling A2A mark task complete: {e}")
            return web.json_response(
                {
                    "success": False,
                    "error": str(e),
                    "protocol": "A2A"
                },
                status=500
            )

    async def handle_a2a_delete_task(self, request: web.Request) -> web.Response:
        """Handle A2A delete task requests."""
        try:
            data = await request.json()
            task_id = data.get("task_id", "")
            
            if not task_id:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Task ID is required",
                        "protocol": "A2A"
                    },
                    status=400
                )
            
            if "delete_task" in self.handlers:
                result = await self.handlers["delete_task"](task_id)
                return web.json_response({
                    "success": True,
                    "result": result,
                    "protocol": "A2A"
                })
            else:
                return web.json_response(
                    {
                        "success": False,
                        "error": "Delete task handler not registered",
                        "protocol": "A2A"
                    },
                    status=501
                )
        except Exception as e:
            logger.error(f"Error handling A2A delete task: {e}")
            return web.json_response(
                {
                    "success": False,
                    "error": str(e),
                    "protocol": "A2A"
                },
                status=500
            )

    async def handle_a2a_health(self, request: web.Request) -> web.Response:
        """Handle A2A health check requests."""
        return web.json_response({
            "status": "healthy",
            "service": "A2A Server",
            "protocol": "A2A",
            "version": "1.0.0",
            "capabilities": list(self.handlers.keys())
        })

    async def handle_a2a_capabilities(self, request: web.Request) -> web.Response:
        """Handle A2A capabilities requests."""
        capabilities = [
            {
                "method": "add_task",
                "description": "Add a new task",
                "parameters": {
                    "description": {"type": "string", "required": True}
                }
            },
            {
                "method": "list_tasks",
                "description": "List all tasks",
                "parameters": {}
            },
            {
                "method": "mark_task_complete",
                "description": "Mark a task as complete",
                "parameters": {
                    "task_id": {"type": "string", "required": True}
                }
            },
            {
                "method": "delete_task",
                "description": "Delete a task",
                "parameters": {
                    "task_id": {"type": "string", "required": True}
                }
            }
        ]
        
        return web.json_response({
            "protocol": "A2A",
            "capabilities": capabilities,
            "registered_handlers": list(self.handlers.keys())
        })

    async def start(self) -> None:
        """Start the A2A server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        logger.info(f"A2A Server started at http://{self.host}:{self.port}")
        
        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down A2A Server...")
        finally:
            await runner.cleanup()

    def run(self) -> None:
        """Run the A2A server."""
        asyncio.run(self.start())


class A2AClient:
    """A2A client for communicating with A2A servers."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        """Initialize the A2A client."""
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    async def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a request to the A2A server."""
        if not self.session:
            raise RuntimeError("A2AClient not initialized. Use async context manager or call connect() first.")

        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except aiohttp.ClientError as e:
            logger.error(f"A2A HTTP request failed: {e}")
            return {"success": False, "error": f"A2A HTTP request failed: {e}"}
        except json.JSONDecodeError as e:
            logger.error(f"A2A JSON decode error: {e}")
            return {"success": False, "error": f"Invalid A2A JSON response: {e}"}
        except Exception as e:
            logger.error(f"A2A unexpected error: {e}")
            return {"success": False, "error": f"A2A unexpected error: {e}"}

    async def connect(self) -> None:
        """Connect to the A2A server."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def disconnect(self) -> None:
        """Disconnect from the A2A server."""
        if self.session:
            await self.session.close()
            self.session = None

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the A2A server."""
        return await self._make_request("GET", "/a2a/health")

    async def get_capabilities(self) -> Dict[str, Any]:
        """Get the capabilities of the A2A server."""
        return await self._make_request("GET", "/a2a/capabilities")

    async def add_task(self, description: str) -> Dict[str, Any]:
        """Add a new task via A2A."""
        data = {"description": description}
        return await self._make_request("POST", "/a2a/add_task", data)

    async def list_tasks(self) -> Dict[str, Any]:
        """List all tasks via A2A."""
        return await self._make_request("GET", "/a2a/list_tasks")

    async def mark_task_complete(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as complete via A2A."""
        data = {"task_id": task_id}
        return await self._make_request("POST", "/a2a/mark_task_complete", data)

    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task via A2A."""
        data = {"task_id": task_id}
        return await self._make_request("POST", "/a2a/delete_task", data)

    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.session is not None and not self.session.closed 