"""Task data store implementation using SQLite."""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TaskStore:
    """SQLite-based task storage implementation."""

    def __init__(self, db_path: str = "./data/tasks.db"):
        """Initialize the task store with the specified database path."""
        self.db_path = db_path
        self._ensure_data_directory()
        self.init_db()

    def _ensure_data_directory(self) -> None:
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def init_db(self) -> None:
        """Initialize the database with the tasks table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        description TEXT NOT NULL,
                        status TEXT NOT NULL DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def add_task(self, description: str) -> Dict:
        """Add a new task to the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO tasks (description, status) VALUES (?, ?)",
                    (description, "pending")
                )
                task_id = cursor.lastrowid
                conn.commit()
                
                # Fetch the created task
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task = cursor.fetchone()
                
                return {
                    "id": task[0],
                    "description": task[1],
                    "status": task[2],
                    "created_at": task[3]
                }
        except sqlite3.Error as e:
            logger.error(f"Failed to add task: {e}")
            raise

    def list_tasks(self) -> List[Dict]:
        """Retrieve all tasks from the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
                tasks = cursor.fetchall()
                
                return [
                    {
                        "id": task[0],
                        "description": task[1],
                        "status": task[2],
                        "created_at": task[3]
                    }
                    for task in tasks
                ]
        except sqlite3.Error as e:
            logger.error(f"Failed to list tasks: {e}")
            raise

    def get_task(self, task_id: int) -> Optional[Dict]:
        """Retrieve a specific task by ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task = cursor.fetchone()
                
                if task:
                    return {
                        "id": task[0],
                        "description": task[1],
                        "status": task[2],
                        "created_at": task[3]
                    }
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get task {task_id}: {e}")
            raise

    def mark_task_complete(self, task_id: int) -> Optional[Dict]:
        """Mark a task as complete."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    ("completed", task_id)
                )
                
                if cursor.rowcount == 0:
                    return None
                
                conn.commit()
                
                # Fetch the updated task
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task = cursor.fetchone()
                
                return {
                    "id": task[0],
                    "description": task[1],
                    "status": task[2],
                    "created_at": task[3]
                }
        except sqlite3.Error as e:
            logger.error(f"Failed to mark task {task_id} complete: {e}")
            raise

    def delete_task(self, task_id: int) -> Optional[Dict]:
        """Delete a specific task."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First, get the task to return it
                cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
                task = cursor.fetchone()
                
                if not task:
                    return None
                
                # Delete the task
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                
                return {
                    "id": task[0],
                    "description": task[1],
                    "status": task[2],
                    "created_at": task[3]
                }
        except sqlite3.Error as e:
            logger.error(f"Failed to delete task {task_id}: {e}")
            raise

    def clear_all_tasks(self) -> Dict:
        """Delete all tasks from the store."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks")
                deleted_count = cursor.rowcount
                conn.commit()
                
                return {
                    "message": f"Deleted {deleted_count} tasks",
                    "deleted_count": deleted_count
                }
        except sqlite3.Error as e:
            logger.error(f"Failed to clear all tasks: {e}")
            raise

    def get_task_count(self) -> int:
        """Get the total number of tasks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM tasks")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Failed to get task count: {e}")
            raise 