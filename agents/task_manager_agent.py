"""Task Manager Agent implementation."""

import asyncio
import logging
import threading
import sys
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent
from protocols.mcp_client import MCPClientSync, MCPClient
from protocols.a2a_server import A2AServer
import os

logger = logging.getLogger(__name__)


class TaskManagerAgent(BaseAgent):
    """Task Manager Agent that handles task operations and A2A requests."""

    def __init__(self):
        """Initialize the Task Manager Agent."""
        super().__init__("TaskManagerAgent")
        self.mcp_client = MCPClientSync()
        self.mcp_client_async = MCPClient()
        self.a2a_server = A2AServer()
        self.setup_a2a_handlers()

    def setup_a2a_handlers(self) -> None:
        """Setup A2A handlers for inter-agent communication."""
        self.a2a_server.register_handler("add_task", self.handle_a2a_add_task)
        self.a2a_server.register_handler("list_tasks", self.handle_a2a_list_tasks)
        self.a2a_server.register_handler("mark_task_complete", self.handle_a2a_mark_task_complete)
        self.a2a_server.register_handler("delete_task", self.handle_a2a_delete_task)
        self.log_info("A2A handlers registered")

    async def handle_a2a_add_task(self, description: str) -> Dict[str, Any]:
        """Handle A2A add task request (async)."""
        try:
            self.log_info(f"A2A request: add task '{description}'")
            async with self.mcp_client_async as client:
                result = await client.add_task(description)
            if result.get("success"):
                task = result.get("task", {})
                self.log_info(f"A2A response: Task added successfully (ID: {task.get('id')})")
                return result
            else:
                self.log_error(f"A2A response: Failed to add task - {result.get('error')}")
                return result
        except Exception as e:
            return self.handle_error(e, "A2A add task")

    async def handle_a2a_list_tasks(self) -> Dict[str, Any]:
        """Handle A2A list tasks request (async)."""
        try:
            self.log_info("A2A request: list tasks")
            async with self.mcp_client_async as client:
                result = await client.list_tasks()
            if result.get("success"):
                tasks = result.get("tasks", [])
                self.log_info(f"A2A response: Retrieved {len(tasks)} tasks")
                return result
            else:
                self.log_error(f"A2A response: Failed to list tasks - {result.get('error')}")
                return result
        except Exception as e:
            return self.handle_error(e, "A2A list tasks")

    async def handle_a2a_mark_task_complete(self, task_id: str) -> Dict[str, Any]:
        """Handle A2A mark task complete request (async)."""
        try:
            self.log_info(f"A2A request: mark task {task_id} complete")
            async with self.mcp_client_async as client:
                result = await client.mark_task_complete(task_id)
            if result.get("success"):
                self.log_info(f"A2A response: Task {task_id} marked as complete")
                return result
            else:
                self.log_error(f"A2A response: Failed to mark task {task_id} complete - {result.get('error')}")
                return result
        except Exception as e:
            return self.handle_error(e, "A2A mark task complete")

    async def handle_a2a_delete_task(self, task_id: str) -> Dict[str, Any]:
        """Handle A2A delete task request (async)."""
        try:
            self.log_info(f"A2A request: delete task {task_id}")
            async with self.mcp_client_async as client:
                result = await client.delete_task(task_id)
            if result.get("success"):
                self.log_info(f"A2A response: Task {task_id} deleted successfully")
                return result
            else:
                self.log_error(f"A2A response: Failed to delete task {task_id} - {result.get('error')}")
                return result
        except Exception as e:
            return self.handle_error(e, "A2A delete task")

    def add_task(self, description: str) -> Dict[str, Any]:
        """Add a new task."""
        try:
            if not self.validate_input(description, str, "description"):
                return self.format_response(False, "Invalid task description")

            self.log_info(f"Adding task: {description}")
            result = self.mcp_client.add_task(description)
            
            if result.get("success"):
                task = result.get("task", {})
                message = f"Task '{description}' (ID: {task.get('id')}) added successfully."
                self.log_info(message)
                return self.format_response(True, message, task)
            else:
                error_msg = f"Failed to add task: {result.get('error')}"
                self.log_error(error_msg)
                return self.format_response(False, error_msg)
        except Exception as e:
            return self.handle_error(e, "add task")

    def list_tasks(self) -> Dict[str, Any]:
        """List all tasks."""
        try:
            self.log_info("Listing all tasks")
            result = self.mcp_client.list_tasks()
            
            if result.get("success"):
                tasks = result.get("tasks", [])
                message = f"Retrieved {len(tasks)} tasks"
                self.log_info(message)
                return self.format_response(True, message, {"tasks": tasks})
            else:
                error_msg = f"Failed to list tasks: {result.get('error')}"
                self.log_error(error_msg)
                return self.format_response(False, error_msg)
        except Exception as e:
            return self.handle_error(e, "list tasks")

    def mark_task_complete(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as complete."""
        try:
            if not self.validate_input(task_id, str, "task_id"):
                return self.format_response(False, "Invalid task ID")

            self.log_info(f"Marking task {task_id} as complete")
            result = self.mcp_client.mark_task_complete(task_id)
            
            if result.get("success"):
                task = result.get("task", {})
                message = f"Task {task_id} marked as complete"
                self.log_info(message)
                return self.format_response(True, message, task)
            else:
                error_msg = f"Failed to mark task {task_id} complete: {result.get('error')}"
                self.log_error(error_msg)
                return self.format_response(False, error_msg)
        except Exception as e:
            return self.handle_error(e, "mark task complete")

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task."""
        try:
            if not self.validate_input(task_id, str, "task_id"):
                return self.format_response(False, "Invalid task ID")

            self.log_info(f"Deleting task {task_id}")
            result = self.mcp_client.delete_task(task_id)
            
            if result.get("success"):
                task = result.get("task", {})
                message = f"Task {task_id} deleted successfully"
                self.log_info(message)
                return self.format_response(True, message, task)
            else:
                error_msg = f"Failed to delete task {task_id}: {result.get('error')}"
                self.log_error(error_msg)
                return self.format_response(False, error_msg)
        except Exception as e:
            return self.handle_error(e, "delete task")

    def clear_all_tasks(self) -> Dict[str, Any]:
        """Clear all tasks."""
        try:
            self.log_info("Clearing all tasks")
            result = self.mcp_client.clear_all_tasks()
            
            if result.get("success"):
                clear_result = result.get("result", {})
                message = clear_result.get("message", "All tasks cleared")
                self.log_info(message)
                return self.format_response(True, message, clear_result)
            else:
                error_msg = f"Failed to clear all tasks: {result.get('error')}"
                self.log_error(error_msg)
                return self.format_response(False, error_msg)
        except Exception as e:
            return self.handle_error(e, "clear all tasks")

    def get_task_count(self) -> Dict[str, Any]:
        """Get the total number of tasks."""
        try:
            self.log_info("Getting task count")
            result = self.mcp_client.get_task_count()
            
            if result.get("success"):
                count = result.get("count", 0)
                message = f"Total tasks: {count}"
                self.log_info(message)
                return self.format_response(True, message, {"count": count})
            else:
                error_msg = f"Failed to get task count: {result.get('error')}"
                self.log_error(error_msg)
                return self.format_response(False, error_msg)
        except Exception as e:
            return self.handle_error(e, "get task count")

    def health_check(self) -> Dict[str, Any]:
        """Check the health of the MCP server."""
        try:
            self.log_info("Checking MCP server health")
            result = self.mcp_client.health_check()
            
            if result.get("status") == "healthy":
                message = "MCP server is healthy"
                self.log_info(message)
                return self.format_response(True, message, result)
            else:
                error_msg = "MCP server is not healthy"
                self.log_error(error_msg)
                return self.format_response(False, error_msg, result)
        except Exception as e:
            return self.handle_error(e, "health check")

    def start_a2a_server(self) -> None:
        """Start the A2A server."""
        self.log_info("Starting A2A server")
        self.a2a_server.run()

    async def start_a2a_server_async(self) -> None:
        """Start the A2A server asynchronously."""
        self.log_info("Starting A2A server asynchronously")
        await self.a2a_server.start() 