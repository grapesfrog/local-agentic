# Quick Start Guide - Multi-Agent Task Manager System

## 🚀 Onboarding Snippet

### Prerequisites
```bash
# Install Ollama (if not already installed)
# See https://ollama.com/download for your OS
ollama serve &
ollama pull gemma3:4b
```

### 1. Setup & Start Services
```bash
# Clone and setup
git clone <repository-url>
cd GDC-agentic
uv sync

# Start all components (in separate terminals)
# Terminal 1: MCP Server (port 8002)
MCP_SERVER_PORT=8002 uv run python mcp_server/task_mcp_server.py

# Terminal 2: Task Manager Agent (A2A server, port 8001)
uv run python cli/task_manager_cli.py

# Terminal 3: Meeting Assistant Agent
uv run python cli/meeting_assistant_cli.py

# Terminal 4: ADK Web UI (port 8000)
uv run adk web
```

### 2. Access Points
- **ADK Web UI**: http://localhost:8000 (recommended)
- **MCP Server**: http://localhost:8002
- **A2A Server**: http://localhost:8001

### 3. Quick Test
```bash
# Test MCP server
curl http://localhost:8002/health

# Test A2A server
curl http://localhost:8001/a2a/health

# Test via ADK Web UI
# Open http://localhost:8000 in browser
```

### 4. Basic Workflow
1. **Via Web UI**: Open http://localhost:8000 → Create/configure agents → Run workflows
2. **Via CLI**: Use the Task Manager and Meeting Assistant CLI interfaces
3. **Via HTTP**: Direct API calls to MCP (port 8002) and A2A (port 8001) endpoints

### 5. Example Usage
```bash
# Add task via MCP
curl -X POST http://localhost:8002/tools/add_task \
  -H "Content-Type: application/json" \
  -d '{"description": "Complete quarterly report"}'

# Process meeting notes via Meeting Assistant CLI
# In Meeting Assistant terminal:
process notes 'Team meeting. Action: Email John about budget. Follow up: Schedule next meeting.'
```

## 📋 Port Summary
| Service | Port | Purpose |
|---------|------|---------|
| ADK Web UI | 8000 | Main interface for agent orchestration |
| A2A Server | 8001 | Inter-agent communication |
| MCP Server | 8002 | Task management tools |

## 🔧 Troubleshooting
- **Port conflicts**: Check `lsof -i :8000/8001/8002`
- **Ollama not running**: Start with `ollama serve`
- **Import errors**: Ensure you're in the project directory and using `uv run`

## 📚 Next Steps
- Read the full [README.md](README.md) for detailed setup
- Check [ADK_TESTING_GUIDE.md](ADK_TESTING_GUIDE.md) for testing workflows
- Explore the ADK Web UI for advanced agent configuration 

## End-to-End System Test

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