# Scripts Directory

This directory contains utility scripts for managing and testing the On-Premises Multi-Agent Task Manager System.

## 📋 Available Scripts

### Service Management

#### `start_all.py`
Comprehensive script to start all system services.

**Usage:**
```bash
# Start all services
uv run python scripts/start_all.py

# Start with ADK web interface
uv run python scripts/start_all.py --web

# Start with demo
uv run python scripts/start_all.py --demo
```

**Features:**
- Checks Ollama availability
- Starts MCP server on port 8002
- Starts Task Manager Agent with A2A server on port 8001
- Starts Meeting Assistant Agent
- Optionally starts ADK web interface on port 8000
- Runs demo script if requested
- Monitors all processes

#### `stop_all.py`
Gracefully shuts down all running services.

**Usage:**
```bash
uv run python scripts/stop_all.py
```

**Features:**
- Stops ADK web interface
- Stops Meeting Assistant Agent
- Stops Task Manager Agent
- Stops A2A server
- Stops MCP server
- Cleans up temporary files
- Verifies ports are available
- Checks Ollama status (doesn't stop it)

#### `start_env.py`
Quick environment setup script.

**Usage:**
```bash
uv run python scripts/start_env.py
```

**Features:**
- Creates data directory
- Copies environment file
- Initializes database
- Checks basic dependencies

#### `stop_env.py`
Environment cleanup script.

**Usage:**
```bash
uv run python scripts/stop_env.py
```

**Features:**
- Stops running services
- Cleans up temporary files
- Resets environment state

### Testing and Health Checks

#### `quick_test.py`
Performs basic functionality tests.

**Usage:**
```bash
uv run python scripts/quick_test.py
```

**Tests:**
- Environment configuration
- Database functionality
- MCP server connectivity
- Task operations via MCP

**Output:**
- Pass/fail status for each test
- Detailed error messages
- Overall system readiness assessment

#### `health_check.py`
Comprehensive system health check.

**Usage:**
```bash
uv run python scripts/health_check.py
```

**Checks:**
- Environment configuration
- Python dependencies
- Data directory and files
- Database connectivity
- Ollama availability
- MCP server health
- A2A server health

**Output:**
- Detailed health status for each component
- Troubleshooting recommendations
- Next steps for system usage

#### `run_demo.py`
Complete system demonstration.

**Usage:**
```bash
uv run python scripts/run_demo.py
```

**Demonstrates:**
- MCP server operations
- Task Manager Agent capabilities
- Meeting Assistant Agent functionality
- Inter-agent communication via A2A
- MCP tool integration

**Features:**
- Starts all required services
- Runs comprehensive demonstrations
- Shows real-time system interactions
- Provides usage instructions

### End-to-End System Test

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

## 🚀 Quick Start Workflow

### 1. Initial Setup
```bash
# Check system health
uv run python scripts/health_check.py

# Setup environment
uv run python scripts/start_env.py
```

### 2. Start Services
```bash
# Start all services
uv run python scripts/start_all.py --web

# Or start individually
uv run python mcp_server/task_mcp_server.py
uv run python cli/task_manager_cli.py
uv run python cli/meeting_assistant_cli.py
uv run adk web
```

### 3. Testing
```bash
# Quick functionality test
uv run python scripts/quick_test.py

# Run complete demo
uv run python scripts/run_demo.py
```

### 4. Stop Services
```bash
# Stop all services
uv run python scripts/stop_all.py
```

## 🔧 Development Workflow

### Daily Development
```bash
# 1. Check system health
uv run python scripts/health_check.py

# 2. Start services for development
uv run python scripts/start_all.py --web

# 3. Make changes and test

# 4. Run quick tests
uv run python scripts/quick_test.py

# 5. Stop services when done
uv run python scripts/stop_all.py
```

### Troubleshooting
```bash
# Check what's running
uv run python scripts/health_check.py

# Force stop everything
uv run python scripts/stop_all.py

# Clean restart
uv run python scripts/start_all.py
```

## 📊 Script Dependencies

### Required Python Packages
- `requests` - HTTP client for health checks
- `psutil` - Process management for stop_all.py
- `aiohttp` - Async HTTP server (for MCP server)
- `python-dotenv` - Environment variable management

### System Requirements
- Python 3.9+
- Ollama (for LLM inference)
- Network access for localhost ports

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8002
   
   # Stop conflicting services
   uv run python scripts/stop_all.py
   ```

2. **Ollama Not Responding**
   ```bash
   # Check Ollama status
   ollama list
   
   # Restart Ollama
   ollama serve --stop
   ollama serve &
   ```

3. **Database Errors**
   ```bash
   # Reinitialize database
   python -c "from data_store.task_store import TaskStore; TaskStore().init_db()"
   ```

4. **Environment Issues**
   ```bash
   # Reset environment
   uv run python scripts/stop_env.py
   uv run python scripts/start_env.py
   ```

### Script-Specific Issues

#### `stop_all.py` Fails
- May need elevated permissions on some systems
- Some processes might be protected
- Use `kill -9` manually if needed

#### `health_check.py` Shows Warnings
- Some warnings are normal (e.g., A2A health endpoint)
- Check the specific component that's failing
- Verify environment variables are set correctly

#### `run_demo.py` Times Out
- Increase timeout values in the script
- Check if all services are starting properly
- Verify network connectivity

## 📝 Script Customization

### Environment Variables
All scripts respect the following environment variables:
- `MCP_SERVER_PORT` - MCP server port (default: 8002)
- `A2A_SERVER_PORT` - A2A server port (default: 8001)
- `DEBUG` - Enable debug logging
- `LOG_LEVEL` - Logging level

### Custom Ports
To use different ports:
```bash
export MCP_SERVER_PORT=8003
export A2A_SERVER_PORT=8004
uv run python scripts/start_all.py
```

### Debug Mode
Enable debug logging:
```bash
export DEBUG=1
export LOG_LEVEL=DEBUG
uv run python scripts/health_check.py
```

## 🤝 Contributing

This is purely for demo purposes so I am not accepting contributions . Fork and have fun with it I did!

### Script Template
```python
#!/usr/bin/env python3
"""
Script description.

Usage:
    python scripts/script_name.py [options]
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main function."""
    # Implementation here
    pass

if __name__ == "__main__":
    sys.exit(main()) 