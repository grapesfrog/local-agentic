import subprocess
import time
import requests
import os
import pytest

# Adjust these as needed for your environment
TASK_MANAGER_CMD = ["python", "run_task_manager.py"]
MCP_SERVER_CMD = ["python", "start_mcp_server.py"]

@pytest.fixture(scope="module", autouse=True)
def start_services():
    # Start MCP server
    mcp_proc = subprocess.Popen(MCP_SERVER_CMD)
    time.sleep(2)  # Wait for server to start
    # Start Task Manager
    tm_proc = subprocess.Popen(TASK_MANAGER_CMD)
    time.sleep(2)
    yield
    mcp_proc.terminate()
    tm_proc.terminate()
    mcp_proc.wait()
    tm_proc.wait()

def test_task_creation_and_completion():
    # Example: Simulate a task creation via HTTP or CLI, then check DB or output
    # This is a placeholder; adapt to your actual API/CLI
    assert os.path.exists("data/tasks.db") 