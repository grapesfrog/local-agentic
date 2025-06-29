"""MCP tools for task management operations."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from typing import Dict, List, Any
from data_store.task_store import TaskStore
import logging

logger = logging.getLogger(__name__)


class TaskTools:
    """MCP tools for task management operations."""

    def __init__(self, task_store: TaskStore):
        """Initialize the task tools with a task store."""
        self.task_store = task_store

    def add_task(self, description: str) -> Dict[str, Any]:
        """Add a new task to the store."""
        try:
            task = self.task_store.add_task(description)
            return {
                "success": True,
                "task": task,
                "message": f"Task '{description}' (ID: {task['id']}) added successfully."
            }
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to add task: {e}"
            }

    def list_tasks(self) -> Dict[str, Any]:
        """Retrieve all tasks from the store."""
        try:
            tasks = self.task_store.list_tasks()
            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks),
                "message": f"Retrieved {len(tasks)} tasks."
            }
        except Exception as e:
            logger.error(f"Failed to list tasks: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list tasks: {e}"
            }

    def mark_task_complete(self, task_id: str) -> Dict[str, Any]:
        """Mark a task as complete."""
        try:
            task_id_int = int(task_id)
            task = self.task_store.mark_task_complete(task_id_int)
            
            if task:
                return {
                    "success": True,
                    "task": task,
                    "message": f"Task {task_id} marked as complete."
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} not found."
                }
        except ValueError:
            return {
                "success": False,
                "error": "Invalid task ID",
                "message": f"Invalid task ID: {task_id}. Must be a number."
            }
        except Exception as e:
            logger.error(f"Failed to mark task {task_id} complete: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to mark task {task_id} complete: {e}"
            }

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a specific task."""
        try:
            task_id_int = int(task_id)
            task = self.task_store.delete_task(task_id_int)
            
            if task:
                return {
                    "success": True,
                    "task": task,
                    "message": f"Task {task_id} deleted successfully."
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} not found."
                }
        except ValueError:
            return {
                "success": False,
                "error": "Invalid task ID",
                "message": f"Invalid task ID: {task_id}. Must be a number."
            }
        except Exception as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete task {task_id}: {e}"
            }

    def clear_all_tasks(self) -> Dict[str, Any]:
        """Delete all tasks from the store."""
        try:
            result = self.task_store.clear_all_tasks()
            return {
                "success": True,
                "result": result,
                "message": result["message"]
            }
        except Exception as e:
            logger.error(f"Failed to clear all tasks: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to clear all tasks: {e}"
            }

    def get_task_count(self) -> Dict[str, Any]:
        """Get the total number of tasks."""
        try:
            count = self.task_store.get_task_count()
            return {
                "success": True,
                "count": count,
                "message": f"Total tasks: {count}"
            }
        except Exception as e:
            logger.error(f"Failed to get task count: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get task count: {e}"
            }

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID."""
        try:
            task_id_int = int(task_id)
            task = self.task_store.get_task(task_id_int)
            
            if task:
                return {
                    "success": True,
                    "task": task,
                    "message": f"Retrieved task {task_id}."
                }
            else:
                return {
                    "success": False,
                    "error": "Task not found",
                    "message": f"Task {task_id} not found."
                }
        except ValueError:
            return {
                "success": False,
                "error": "Invalid task ID",
                "message": f"Invalid task ID: {task_id}. Must be a number."
            }
        except Exception as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get task {task_id}: {e}"
            } 