"""Tests for the Task Manager Agent."""

import pytest
import tempfile
import os
from agents.task_manager_agent import TaskManagerAgent
from data_store.task_store import TaskStore


class TestTaskManagerAgent:
    """Test cases for TaskManagerAgent."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    def task_store(self, temp_db):
        """Create a TaskStore instance with temporary database."""
        return TaskStore(db_path=temp_db)

    @pytest.fixture
    def agent(self):
        """Create a TaskManagerAgent instance."""
        return TaskManagerAgent()

    def test_agent_initialization(self, agent):
        """Test that the agent initializes correctly."""
        assert agent.name == "TaskManagerAgent"
        assert agent.mcp_client is not None
        assert agent.a2a_server is not None

    def test_add_task(self, task_store):
        """Test adding a task."""
        description = "Test task"
        result = task_store.add_task(description)
        
        assert result["description"] == description
        assert result["status"] == "pending"
        assert "id" in result
        assert "created_at" in result

    def test_list_tasks(self, task_store):
        """Test listing tasks."""
        # Add some tasks
        task_store.add_task("Task 1")
        task_store.add_task("Task 2")
        
        tasks = task_store.list_tasks()
        assert len(tasks) == 2
        assert tasks[0]["description"] == "Task 2"  # Most recent first
        assert tasks[1]["description"] == "Task 1"

    def test_mark_task_complete(self, task_store):
        """Test marking a task as complete."""
        # Add a task
        task = task_store.add_task("Test task")
        task_id = task["id"]
        
        # Mark as complete
        result = task_store.mark_task_complete(task_id)
        assert result["status"] == "completed"
        assert result["id"] == task_id

    def test_delete_task(self, task_store):
        """Test deleting a task."""
        # Add a task
        task = task_store.add_task("Test task")
        task_id = task["id"]
        
        # Delete the task
        result = task_store.delete_task(task_id)
        assert result["id"] == task_id
        
        # Verify it's gone
        tasks = task_store.list_tasks()
        assert len(tasks) == 0

    def test_clear_all_tasks(self, task_store):
        """Test clearing all tasks."""
        # Add some tasks
        task_store.add_task("Task 1")
        task_store.add_task("Task 2")
        
        # Clear all tasks
        result = task_store.clear_all_tasks()
        assert result["deleted_count"] == 2
        
        # Verify they're gone
        tasks = task_store.list_tasks()
        assert len(tasks) == 0

    def test_get_task_count(self, task_store):
        """Test getting task count."""
        # Initially should be 0
        assert task_store.get_task_count() == 0
        
        # Add some tasks
        task_store.add_task("Task 1")
        task_store.add_task("Task 2")
        
        # Should be 2
        assert task_store.get_task_count() == 2

    def test_get_task(self, task_store):
        """Test getting a specific task."""
        # Add a task
        original_task = task_store.add_task("Test task")
        task_id = original_task["id"]
        
        # Get the task
        retrieved_task = task_store.get_task(task_id)
        assert retrieved_task["id"] == task_id
        assert retrieved_task["description"] == "Test task"
        
        # Test getting non-existent task
        non_existent = task_store.get_task(999)
        assert non_existent is None 