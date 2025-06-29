"""Task Manager CLI implementation."""

import asyncio
import threading
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from agents.task_manager_agent import TaskManagerAgent
import logging

logger = logging.getLogger(__name__)


class TaskManagerCLI:
    """Command-line interface for the Task Manager Agent."""

    def __init__(self):
        """Initialize the Task Manager CLI."""
        self.agent = TaskManagerAgent()
        self.running = False

    def show_help(self) -> None:
        """Display help information."""
        help_text = """
Task Manager Agent - Available Commands:

  add 'description'     - Add a new task with the given description
  list tasks           - Show all tasks
  complete <task_id>   - Mark a task as complete
  delete <task_id>     - Delete a task
  clear all tasks      - Delete all tasks
  count                - Show the total number of tasks
  health               - Check MCP server health
  help                 - Show this help message
  quit                 - Exit the application

Examples:
  add 'Submit weekly report'
  add 'Review budget figures'
  list tasks
  complete 1
  delete 2
  clear all tasks
"""
        print(help_text)

    def parse_command(self, command: str) -> Dict[str, Any]:
        """Parse a command string and return the parsed components."""
        parts = command.strip().split()
        if not parts:
            return {"command": "empty", "args": []}

        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        return {"command": cmd, "args": args}

    def handle_add_task(self, args: list) -> None:
        """Handle the add task command."""
        if not args:
            print("Error: Task description is required")
            print("Usage: add 'Task description'")
            return

        # Join all arguments as the description
        description = " ".join(args)
        
        # Remove quotes if present
        if (description.startswith("'") and description.endswith("'")) or \
           (description.startswith('"') and description.endswith('"')):
            description = description[1:-1]

        if not description.strip():
            print("Error: Task description cannot be empty")
            return

        result = self.agent.add_task(description)
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ {result.get('message')}")

    def handle_list_tasks(self, args: list) -> None:
        """Handle the list tasks command."""
        if args:
            print("Warning: 'list tasks' command doesn't take arguments")
        
        result = self.agent.list_tasks()
        if result.get("success"):
            tasks = result.get("data", {}).get("tasks", [])
            if tasks:
                print("\nTasks:")
                print("-" * 50)
                for task in tasks:
                    status_icon = "✓" if task.get("status") == "completed" else "○"
                    print(f"{status_icon} {task.get('id')}. {task.get('description')} ({task.get('status')})")
                print("-" * 50)
            else:
                print("No tasks found.")
        else:
            print(f"✗ {result.get('message')}")

    def handle_complete_task(self, args: list) -> None:
        """Handle the complete task command."""
        if not args:
            print("Error: Task ID is required")
            print("Usage: complete <task_id>")
            return

        if len(args) > 1:
            print("Warning: Only the first argument will be used as task ID")

        task_id = args[0]
        result = self.agent.mark_task_complete(task_id)
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ {result.get('message')}")

    def handle_delete_task(self, args: list) -> None:
        """Handle the delete task command."""
        if not args:
            print("Error: Task ID is required")
            print("Usage: delete <task_id>")
            return

        if len(args) > 1:
            print("Warning: Only the first argument will be used as task ID")

        task_id = args[0]
        result = self.agent.delete_task(task_id)
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ {result.get('message')}")

    def handle_clear_all_tasks(self, args: list) -> None:
        """Handle the clear all tasks command."""
        if args:
            print("Warning: 'clear all tasks' command doesn't take arguments")
        
        # Ask for confirmation
        confirm = input("Are you sure you want to delete all tasks? (yes/no): ").lower().strip()
        if confirm in ['yes', 'y']:
            result = self.agent.clear_all_tasks()
            if result.get("success"):
                print(f"✓ {result.get('message')}")
            else:
                print(f"✗ {result.get('message')}")
        else:
            print("Operation cancelled.")

    def handle_count_tasks(self, args: list) -> None:
        """Handle the count tasks command."""
        if args:
            print("Warning: 'count' command doesn't take arguments")
        
        result = self.agent.get_task_count()
        if result.get("success"):
            count = result.get("data", {}).get("count", 0)
            print(f"Total tasks: {count}")
        else:
            print(f"✗ {result.get('message')}")

    def handle_health_check(self, args: list) -> None:
        """Handle the health check command."""
        if args:
            print("Warning: 'health' command doesn't take arguments")
        
        result = self.agent.health_check()
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ {result.get('message')}")

    def process_command(self, command: str) -> bool:
        """Process a command and return True if the application should continue."""
        parsed = self.parse_command(command)
        cmd = parsed["command"]
        args = parsed["args"]

        if cmd == "empty":
            return True
        elif cmd == "quit" or cmd == "exit":
            print("Goodbye!")
            return False
        elif cmd == "help":
            self.show_help()
        elif cmd == "add":
            self.handle_add_task(args)
        elif cmd == "list" and args and args[0] == "tasks":
            self.handle_list_tasks(args[1:])
        elif cmd == "complete":
            self.handle_complete_task(args)
        elif cmd == "delete":
            self.handle_delete_task(args)
        elif cmd == "clear" and len(args) >= 2 and args[0] == "all" and args[1] == "tasks":
            self.handle_clear_all_tasks(args[2:])
        elif cmd == "count":
            self.handle_count_tasks(args)
        elif cmd == "health":
            self.handle_health_check(args)
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")

        return True

    def start_a2a_server_background(self) -> None:
        """Start the A2A server in a background thread."""
        def run_server():
            self.agent.start_a2a_server()

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        print("A2A server started in background")

    def run(self) -> None:
        """Run the CLI application."""
        print("=" * 60)
        print("Task Manager Agent")
        print("=" * 60)
        print("Type 'help' for available commands")
        print("Type 'quit' to exit")
        print()

        # Start A2A server in background
        self.start_a2a_server_background()

        self.running = True
        while self.running:
            try:
                command = input("Task Manager Agent> ").strip()
                if not self.process_command(command):
                    break
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit gracefully")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main function to run the Task Manager CLI."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cli = TaskManagerCLI()
    cli.run()


if __name__ == "__main__":
    main() 