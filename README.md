# Local Multi-Agent Task Manager System

A prototype implementation of a self-contained, local multi-agent task management system that demonstrates collaborative capabilities using Python, Agent Development Kit (ADK), Model Context Protocol (MCP), and Agent2Agent (A2A) protocols.

## 🏗️ Architecture Overview

The system consists of four main components:

- **Task Manager Agent**: Handles user CLI commands and A2A requests for task management
- **Local MCP Tool Server**: Exposes task management functionalities as tools
- **Meeting Assistant Agent**: Processes meeting notes and delegates tasks via A2A
- **Local Data Store**: Persistent SQLite storage for tasks
- **ADK Web UI**: Modern web interface for interacting with agents and tools

```
User → ADK Web UI (http://localhost:8000) → Agents (Task Manager, Meeting Assistant)
TaskManagerADKAgent → LocalTaskMCPToolServer (http://localhost:8002)
MeetingAssistantADKAgent → TaskManagerADKAgent (A2A, http://localhost:8001)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- uv (Python package manager)
- Ollama (for local LLM inference)

### Installation

1. **Install uv** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone and setup the project**:
   ```bash
   git clone <repository-url>
   cd local-agentic
   python setup.py
   ```

3. **Or manually setup**:
   ```bash
   uv sync
   mkdir -p data
   cp env.example .env
   ```

4. **Install and start Ollama** (if not already running):
   ```bash
   # See https://ollama.com/download for install instructions
   ollama serve &
   ollama pull mistral:latest
   ```

## 🛠️ Utility Scripts

The project includes comprehensive utility scripts for easy management and testing:

### Service Management

```bash
# Start all services (MCP, Task Manager, Meeting Assistant, ADK Web)
uv run python scripts/start_all.py --web

# Stop all services and clean up
uv run python scripts/stop_all.py

# Start with demo
uv run python scripts/start_all.py --demo
```

### Testing and Health Checks

```bash
# Quick functionality tests
uv run python scripts/quick_test.py

# Comprehensive health check
uv run python scripts/health_check.py

# Full system demo
uv run python scripts/run_demo.py
```

### Development Workflow

```bash
# 1. Check system health
uv run python scripts/health_check.py

# 2. Run quick tests
uv run python scripts/quick_test.py

# 3. Start services for development
uv run python scripts/start_all.py --web

# 4. Make changes and test

# 5. Stop services when done
uv run python scripts/stop_all.py
```

For detailed information about all available scripts, see [scripts/README.md](scripts/README.md).

## 🛠️ Setup Instructions

### 1. Start the MCP Server (port 8002)

The local MCP server provides task management tools to the Task Manager Agent:

```bash
# Start the MCP server (in one terminal)
MCP_SERVER_PORT=8002 uv run python mcp_server/task_mcp_server.py
```

The MCP server will start on `localhost:8002` and expose the following tools:
- `add_task(description: str)` - Add a new task
- `list_tasks()` - Retrieve all tasks
- `mark_task_complete(task_id: str)` - Mark task as complete
- `delete_task(task_id: str)` - Delete a specific task
- `clear_all_tasks()` - Delete all tasks

### 2. Start the Task Manager Agent (A2A server, port 8001)

```bash
uv run python cli/task_manager_cli.py
```

The A2A server will be available at `http://localhost:8001`.

### 3. Start the Meeting Assistant Agent

```bash
uv run python cli/meeting_assistant_cli.py
```

### 4. Start the ADK Web UI (port 8000)

The ADK web interface provides a modern UI for interacting with your agents and tools:

```bash
uv run adk web
```

Access the web UI at: [http://localhost:8000](http://localhost:8000)

---

## 🖥️ Using the ADK Web UI

- The web UI allows you to create, configure, and interact with agents.
- You can test agent workflows, run evaluation sets, and view logs.
- Agents are configured to use Ollama for local LLM inference (no internet required).
- The UI will automatically discover the MCP and A2A endpoints if the servers are running on the correct ports.

## 📋 Usage

### Task Manager Agent CLI

Start the Task Manager Agent in a new terminal:

```bash
uv run python cli/task_manager_cli.py
```

Available commands:
- `add 'Task description'` - Add a new task
- `list tasks` - Show all tasks
- `complete <task_id>` - Mark task as complete
- `delete <task_id>` - Delete a task
- `clear all tasks` - Delete all tasks
- `count` - Show total number of tasks
- `health` - Check MCP server health
- `help` - Show available commands
- `quit` - Exit the application

Example session:
```
Task Manager Agent> add 'Submit weekly report'
✓ Task 'Submit weekly report' (ID: 1) added successfully.

Task Manager Agent> add 'Review budget figures'
✓ Task 'Review budget figures' (ID: 2) added successfully.

Task Manager Agent> list tasks
Tasks:
--------------------------------------------------
○ 2. Review budget figures (pending)
○ 1. Submit weekly report (pending)
--------------------------------------------------

Task Manager Agent> complete 1
✓ Task 1 marked as complete.

Task Manager Agent> list tasks
Tasks:
--------------------------------------------------
○ 2. Review budget figures (pending)
✓ 1. Submit weekly report (completed)
--------------------------------------------------
```

### Meeting Assistant Agent CLI

Start the Meeting Assistant Agent in another terminal:

```bash
uv run python cli/meeting_assistant_cli.py
```

Available commands:
- `process notes 'Meeting notes text'` - Process meeting notes and delegate tasks
- `process file <filepath>` - Process meeting notes from a file
- `extract 'text'` - Extract action items without delegating
- `keywords` - Show supported action item keywords
- `add keyword <word>` - Add custom keyword
- `remove keyword <word>` - Remove custom keyword
- `capabilities` - Show agent capabilities
- `health` - Check A2A connection health
- `help` - Show available commands
- `quit` - Exit the application

Example session:
```
Meeting Assistant Agent> process notes 'Team meeting discussion. Action: Email John about budget numbers. Follow up: Schedule next meeting with Sarah.'
Processing meeting notes...

✓ Found 2 action items:
  1. Email John about budget numbers
  2. Schedule next meeting with Sarah

✓ Successfully delegated 2 tasks
```

### Demo Script

Run the complete demo to see all components working together:

```bash
uv run python demo.py
```

## 🔧 Configuration

### Environment Variables

The system uses a `.env` file for configuration. Copy the example and modify as needed:

```bash
cp env.example .env
```

Configuration options:
```env
# MCP Server Configuration
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8002

# A2A Configuration
A2A_SERVER_HOST=localhost
A2A_SERVER_PORT=8001

# Database Configuration
DATABASE_PATH=./data/tasks.db

# Logging Configuration
LOG_LEVEL=INFO
DEBUG=false

# Agent Configuration
TASK_MANAGER_AGENT_NAME=TaskManagerAgent
MEETING_ASSISTANT_AGENT_NAME=MeetingAssistantAgent
```

### Database Setup

The system automatically creates the SQLite database on first run:

```bash
# Database will be created at ./data/tasks.db
# You can also manually initialize it:
uv run python -c "from data_store.task_store import TaskStore; TaskStore().init_db()"
```

### Database Reinitialization

To start with a clean database (removes all existing tasks):

```bash
# Remove the existing database file
rm ./data/tasks.db

# Reinitialize the database
uv run python -c "from data_store.task_store import TaskStore; TaskStore().init_db()"
```

**Or use the convenience script**:
```bash
# Interactive mode (asks for confirmation)
uv run python reinit_db.py

# Non-interactive mode (no prompts)
uv run python reinit_db.py --non-interactive

# Force mode (no confirmation)
uv run python reinit_db.py --force
```

**Script options**:
- `--non-interactive`: Run without user prompts (useful for automation)
- `--force`: Skip confirmation and proceed immediately
- No flags: Interactive mode with confirmation prompt

**Benefits of clean database**:
- Start with zero tasks for testing
- Validate all functionality from scratch
- Clear demonstration of system capabilities
- Avoid confusion from existing data
- Ensure consistent test results

### Direct SQLite Database Access

You can directly query the SQLite database to inspect tasks and verify data integrity:

```bash
# Open SQLite shell with the database
sqlite3 ./data/tasks.db

# Or run a single query
sqlite3 ./data/tasks.db "SELECT * FROM tasks;"
```

**Common SQLite Commands**:

```sql
-- Show all tasks
SELECT * FROM tasks;

-- Show tasks with formatted output
SELECT id, description, status, created_at FROM tasks ORDER BY created_at DESC;

-- Count total tasks
SELECT COUNT(*) as total_tasks FROM tasks;

-- Show pending tasks only
SELECT * FROM tasks WHERE status = 'pending';

-- Show completed tasks only
SELECT * FROM tasks WHERE status = 'completed';

-- Show recent tasks (last 10)
SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10;

-- Show task statistics
SELECT 
    status,
    COUNT(*) as count
FROM tasks 
GROUP BY status;

-- Show table schema
.schema tasks

-- Show table info
PRAGMA table_info(tasks);

-- Exit SQLite shell
.quit
```

**One-liner queries**:
```bash
# Quick task count
sqlite3 ./data/tasks.db "SELECT COUNT(*) FROM tasks;"

# List all tasks with status
sqlite3 ./data/tasks.db "SELECT id, description, status FROM tasks ORDER BY id;"

# Check for recent tasks
sqlite3 ./data/tasks.db "SELECT id, description, created_at FROM tasks ORDER BY created_at DESC LIMIT 5;"

# Export tasks to CSV
sqlite3 ./data/tasks.db "SELECT * FROM tasks;" > tasks_export.csv

# Formatted output with headers
echo -e ".mode column\n.headers on\nSELECT id, description, status, created_at FROM tasks ORDER BY id;" | sqlite3 ./data/tasks.db
```

**Database file location**:
- **Path**: `./data/tasks.db`
- **Format**: SQLite 3 database
- **Table**: `tasks`
- **Columns**: `id`, `description`, `status`, `created_at`, `updated_at`

**SQLite Configuration for Better Output**:
```sql
-- Enable column mode for better formatting
.mode column

-- Show column headers
.headers on

-- Set column width for better display
.width 5 30 10 20

-- Show current settings
.show
```

**Useful for**:
- Debugging data issues
- Verifying task operations
- Data validation and testing
- Exporting task data
- Understanding database structure

5. **Clean Database Testing**: For consistent test results, reinitialize the database:
   ```bash
   python reinit_db.py --non-interactive
   ```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=.

# Run specific test file
uv run pytest tests/test_task_manager.py
```

## 📁 Project Structure

```
local-agentic/
├── README.md                 # This file
├── pyproject.toml           # Project configuration and dependencies
├── setup.py                 # Setup script for easy installation
├── demo.py                  # Demo script showing system capabilities
├── env.example              # Example environment configuration
├── example_meeting_notes.txt # Example meeting notes for testing
├── data/                    # Data directory (created automatically)
│   └── tasks.db            # SQLite database (created automatically)
├── mcp_server/             # MCP server implementation
│   ├── __init__.py
│   ├── task_mcp_server.py  # HTTP-based MCP server
│   └── tools.py            # Task management tools
├── agents/                 # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py       # Base agent class
│   ├── task_manager_agent.py # Task Manager Agent
│   └── meeting_assistant_agent.py # Meeting Assistant Agent
├── data_store/             # Data storage layer
│   ├── __init__.py
│   └── task_store.py       # SQLite-based task storage
├── protocols/              # Protocol implementations
│   ├── __init__.py
│   ├── mcp_client.py       # MCP client for agent communication
│   └── a2a_server.py       # A2A server for inter-agent communication
├── cli/                    # Command-line interfaces
│   ├── __init__.py
│   ├── task_manager_cli.py # Task Manager CLI
│   └── meeting_assistant_cli.py # Meeting Assistant CLI
├── scripts/                # Utility scripts
│   ├── README.md           # Scripts documentation
│   ├── start_all.py        # Start all services
│   ├── stop_all.py         # Stop all services
│   ├── start_env.py        # Environment setup
│   ├── stop_env.py         # Environment cleanup
│   ├── quick_test.py       # Quick functionality tests
│   ├── health_check.py     # System health check
│   └── run_demo.py         # Complete system demo
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_task_manager.py # Task Manager tests
│   ├── test_meeting_assistant.py # Meeting Assistant tests
│   ├── test_agents_with_mistral.py # Agent integration tests
│   ├── test_end_to_end.py  # End-to-end tests
│   ├── test_env_file.py    # Environment tests
│   └── test_simple_agent_verification.py # Agent verification tests
├── task_manager_agent/     # ADK Task Manager Agent
│   ├── agent.py            # Agent implementation
│   └── app.yaml            # Agent configuration
├── meeting_assistant_agent/ # ADK Meeting Assistant Agent
│   ├── agent.py            # Agent implementation
│   └── app.yaml            # Agent configuration
├── start_mcp_server.py     # MCP server startup script
├── start_a2a_server.py     # A2A server startup script
├── run_task_manager.py     # Task manager startup script
├── test_adk_integration.py # ADK integration tests
├── test_adk_tools.py       # ADK tools tests
├── test_task_manager.py    # Task manager tests (root level)
├── test_tool_calling.py    # Tool calling validation script
├── reinit_db.py            # Database reinitialization script
├── ADK_TESTING_GUIDE.md    # ADK testing documentation
├── QUICK_START.md          # Quick start guide
├── SETUP_COMPLETE.md       # Setup completion guide
```

## 🔍 Troubleshooting

### Common Issues

1. **MCP Server Connection Failed**:
   - Ensure the MCP server is running: `uv run mcp-server`
   - Check the port configuration in `.env`
   - Verify no other service is using port 8002

2. **Database Errors**:
   - Ensure the `data/` directory exists: `mkdir -p data`
   - Check file permissions for the database file
   - Try reinitializing: `uv run python -c "from data_store.task_store import TaskStore; TaskStore().init_db()"`
   - For clean testing, reinitialize completely: `uv run python reinit_db.py`

3. **A2A Communication Issues**:
   - Verify both agents are running
   - Check network connectivity between localhost ports
   - Ensure Task Manager Agent's A2A server is started

4. **uv Installation Issues**:
   - Update uv: `uv self update`
   - Clear cache: `uv cache clean`
   - Reinstall dependencies: `uv sync --reinstall`

### Debug Mode

Enable debug logging by setting the environment variable:

```bash
export DEBUG=1
uv run task-manager
```

Or modify the `.env` file:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## ⚠️ Known Issues

### Tool Calling Not Working in ADK Web UI

**Issue**: Tool calling functionality may not work properly when using the ADK web interface, even though the LLM integration is functioning correctly.

**Root Cause**: This is a known limitation with the current ADK implementation where tool calling protocols may not be fully compatible with the web UI interface.

**Workarounds**:

#### 1. Command Line Interactive Testing

Use the CLI interfaces to test tool calling functionality:

```bash
# Test Task Manager Agent tool calling
python cli/task_manager_cli.py

# Test Meeting Assistant Agent tool calling
python cli/meeting_assistant_cli.py
```

**Example CLI Testing Session**:
```bash
Task Manager Agent> add 'Test task via CLI'
✓ Task 'Test task via CLI' (ID: 28) added successfully.

Task Manager Agent> list tasks
Tasks:
--------------------------------------------------
○ 28. Test task via CLI (pending)
○ 27. Previous task (pending)
--------------------------------------------------

Task Manager Agent> complete 28
✓ Task 28 marked as complete.

Task Manager Agent> list tasks
Tasks:
--------------------------------------------------
✓ 28. Test task via CLI (completed)
○ 27. Previous task (pending)
--------------------------------------------------
```

#### 2. Automated Test Scripts

Use the provided test scripts to validate functionality:

```bash
# Quick functionality test
python scripts/quick_test.py

# Comprehensive health check
python scripts/health_check.py

# Full system demo with tool calling
python scripts/run_demo.py
```

#### 3. Direct MCP Server Testing

Test tool calling directly against the MCP server:

```bash
# Start MCP server
python mcp_server/task_mcp_server.py

# In another terminal, test with curl
curl -X POST http://localhost:8002/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"description": "Test task via MCP"}'

curl -X GET http://localhost:8002/tools/list_tasks

curl -X POST http://localhost:8002/tools/mark_task_complete \
  -H "Content-Type: application/json" \
  -d '{"task_id": "1"}'
```

#### 4. Python Script Testing

Create a simple Python script to test tool calling:

```python
#!/usr/bin/env python3
"""Test script for MCP tool calling."""

import requests
import json

def test_mcp_tools():
    base_url = "http://localhost:8002/tools"
    
    # Test add task
    response = requests.post(
        f"{base_url}/add_task",
        json={"description": "Python script test task"}
    )
    print(f"Add task response: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test list tasks
    response = requests.get(f"{base_url}/list_tasks")
    print(f"List tasks response: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_mcp_tools()
```

#### 5. Dedicated Tool Calling Test Script

Use the provided `test_tool_calling.py` script for comprehensive tool calling validation:

```bash
# Run the dedicated tool calling test
python test_tool_calling.py
```

This script tests:
- MCP server health
- All MCP tool operations (add, list, complete, delete tasks)
- CLI agent functionality
- Provides detailed feedback and troubleshooting guidance

**Validation Steps**:

1. **Verify LLM Integration**: The ADK web UI can still be used to verify that Ollama and LLM integration are working correctly.

2. **Test Tool Calling**: Use the CLI interfaces or test scripts to validate that tool calling functionality works as expected.

3. **Monitor Logs**: Check the console output of running services for any error messages or debugging information.

4. **Health Check**: Run `python scripts/health_check.py` to ensure all components are functioning properly.

5. **Clean Database Testing**: For consistent test results, reinitialize the database:
   ```bash
   python reinit_db.py --non-interactive
   ```

**Expected Behavior**:
- ADK web UI: LLM responses work, but tool calling may fail
- CLI interfaces: Full functionality including tool calling
- Test scripts: Complete validation of all features
- MCP server: Direct tool calling works correctly

This limitation affects only the web UI interface and does not impact the core functionality of the system. All tool calling features work correctly through the CLI interfaces and direct API calls.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `uv run pytest`
5. Format code: `uv run black .`
6. Commit your changes: `git commit -am 'Add feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## 📄 License

This project is licensed under the Apache License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [uv](https://github.com/astral-sh/uv) for fast Python package management
- Uses [MCP](https://modelcontextprotocol.io/) for tool exposure
- uses [ADK](https://google.github.io/adk-docs/) as the agentic framework
- Implements [A2A](https://github.com/a2aproject/A2A) for inter-agent communication
- Follows ADK principles for agent development
- Based on the requirements document by Grace Mollison 

## 🧪 End-to-End System Test

A comprehensive test script is provided to verify the full workflow, including environment consistency, LLM extraction, tool calling, and task completion:

```bash
uv run python test_end_to_end_delegation.py
```

**This script will:**
- Wait for all services to be up (MCP server, agents, etc.)
- Use the Meeting Assistant agent to process meeting notes and extract tasks using LLM integration
- Delegate the extracted tasks to the Task Manager agent via tool calling
- Verify, via the MCP server HTTP API, that the tasks were created
- Mark a delegated task as complete and verify its status

**What this test covers:**
- All processes use the same environment (via `uv run`)
- LLM extraction and delegation are tested
- Tool calling is verified
- Task completion and status update are verified via the MCP server API

**Expected output:**
- The script prints a summary and exits with success if all steps pass
- If any step fails, it prints an error and exits with a non-zero code

This script is the recommended way to verify that the system is working end-to-end after installation or any major change. 
