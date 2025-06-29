"""MCP client implementation for communicating with the MCP server."""

import aiohttp
import json
from typing import Dict, Any, List, Optional
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class MCPClient:
    """Client for communicating with the MCP server."""

    def __init__(self, base_url: str = "http://localhost:8002"):
        """Initialize the MCP client."""
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
        """Make a request to the MCP server."""
        if not self.session:
            raise RuntimeError("MCPClient not initialized. Use async context manager or call connect() first.")

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
            logger.error(f"HTTP request failed: {e}")
            return {"success": False, "error": f"HTTP request failed: {e}"}
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return {"success": False, "error": f"Invalid JSON response: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": f"Unexpected error: {e}"}

    async def connect(self) -> None:
        """Connect to the MCP server."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def disconnect(self) -> None:
        """Disconnect from the MCP server."""
        if self.session:
            await self.session.close()
            self.session = None

    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the MCP server."""
        return await self._make_request("GET", "/health")

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools from the MCP server."""
        return await self._make_request("GET", "/tools")

    async def add_task(self, description: str) -> Dict[str, Any]:
        """Add a new task via the MCP server."""
        data = {"description": description}
        return await self._make_request("POST", "/tools/add_task", data)

    async def list_tasks(self) -> Dict[str, Any]:
        """List all tasks via the MCP server."""
        return await self._make_request("GET", "/tools/list_tasks")

    async def mark_task_complete(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as complete via the MCP server."""
        data = {"task_id": task_id}
        return await self._make_request("POST", "/tools/mark_task_complete", data)

    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task via the MCP server."""
        data = {"task_id": task_id}
        return await self._make_request("POST", "/tools/delete_task", data)

    async def clear_all_tasks(self) -> Dict[str, Any]:
        """Clear all tasks via the MCP server."""
        return await self._make_request("POST", "/tools/clear_all_tasks")

    async def get_task_count(self) -> Dict[str, Any]:
        """Get the task count via the MCP server."""
        return await self._make_request("GET", "/tools/get_task_count")

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task via the MCP server."""
        return await self._make_request("GET", f"/tools/get_task/{task_id}")

    def is_connected(self) -> bool:
        """Check if the client is connected."""
        return self.session is not None and not self.session.closed


class MCPClientSync:
    """Synchronous wrapper for MCP client."""

    def __init__(self, base_url: str = "http://localhost:8002"):
        """Initialize the synchronous MCP client."""
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    def _make_request_sync(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a synchronous request to the MCP server."""
        import asyncio
        
        async def _async_request():
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}{endpoint}"
                
                try:
                    if method.upper() == "GET":
                        async with session.get(url) as response:
                            return await response.json()
                    elif method.upper() == "POST":
                        async with session.post(url, json=data) as response:
                            return await response.json()
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                except aiohttp.ClientError as e:
                    logger.error(f"HTTP request failed: {e}")
                    return {"success": False, "error": f"HTTP request failed: {e}"}
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    return {"success": False, "error": f"Invalid JSON response: {e}"}
                except Exception as e:
                    logger.error(f"Unexpected error: {e}")
                    return {"success": False, "error": f"Unexpected error: {e}"}

        return asyncio.run(_async_request())

    def health_check(self) -> Dict[str, Any]:
        """Check the health of the MCP server."""
        return self._make_request_sync("GET", "/health")

    def list_tools(self) -> Dict[str, Any]:
        """List available tools from the MCP server."""
        return self._make_request_sync("GET", "/tools")

    def add_task(self, description: str) -> Dict[str, Any]:
        """Add a new task via the MCP server."""
        data = {"description": description}
        return self._make_request_sync("POST", "/tools/add_task", data)

    def list_tasks(self) -> Dict[str, Any]:
        """List all tasks via the MCP server."""
        return self._make_request_sync("GET", "/tools/list_tasks")

    def mark_task_complete(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as complete via the MCP server."""
        data = {"task_id": task_id}
        return self._make_request_sync("POST", "/tools/mark_task_complete", data)

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task via the MCP server."""
        data = {"task_id": task_id}
        return self._make_request_sync("POST", "/tools/delete_task", data)

    def clear_all_tasks(self) -> Dict[str, Any]:
        """Clear all tasks via the MCP server."""
        return self._make_request_sync("POST", "/tools/clear_all_tasks")

    def get_task_count(self) -> Dict[str, Any]:
        """Get the task count via the MCP server."""
        return self._make_request_sync("GET", "/tools/get_task_count")

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task via the MCP server."""
        return self._make_request_sync("GET", f"/tools/get_task/{task_id}") 