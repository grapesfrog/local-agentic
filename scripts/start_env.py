import subprocess
import time

processes = []

# Start MCP server
processes.append(subprocess.Popen(["python", "start_mcp_server.py"]))
time.sleep(2)

# Start Task Manager
processes.append(subprocess.Popen(["python", "run_task_manager.py"]))
time.sleep(2)

# Start ADK Web UI
processes.append(subprocess.Popen(["adk", "web", "--port", "8000"]))
time.sleep(2)

print("Environment started. MCP server, Task Manager agent, and ADK Web UI are running.")
print("ADK Web UI available at: http://localhost:8000") 