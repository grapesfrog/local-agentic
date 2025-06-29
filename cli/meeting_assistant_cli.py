"""Meeting Assistant CLI implementation."""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any
from agents.meeting_assistant_agent import MeetingAssistantAgent
import logging

logger = logging.getLogger(__name__)


class MeetingAssistantCLI:
    """Command-line interface for the Meeting Assistant Agent."""

    def __init__(self):
        """Initialize the Meeting Assistant CLI."""
        self.agent = MeetingAssistantAgent()
        self.running = False

    def show_help(self) -> None:
        """Display help information."""
        help_text = """
Meeting Assistant Agent - Available Commands:

  process notes 'text'   - Process meeting notes text and delegate tasks
  process file <path>    - Process meeting notes from a file
  extract 'text'         - Extract action items from text (without delegating)
  keywords               - Show supported action item keywords
  add keyword <word>     - Add a custom keyword for action item detection
  remove keyword <word>  - Remove a custom keyword
  capabilities           - Show agent capabilities
  health                 - Check A2A connection health
  help                   - Show this help message
  quit                   - Exit the application

Examples:
  process notes 'Team meeting. Action: Email John about budget. Follow up: Schedule next meeting.'
  process file meeting_notes.txt
  extract 'Action: Review quarterly report. TODO: Update project timeline.'
  add keyword 'deadline:'
  remove keyword 'deadline:'
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

    async def handle_process_notes(self, args: list) -> None:
        """Handle the process notes command."""
        if not args:
            print("Error: Meeting notes text is required")
            print("Usage: process notes 'Meeting notes text'")
            return

        # Join all arguments as the notes text
        notes_text = " ".join(args)
        
        # Remove quotes if present
        if (notes_text.startswith("'") and notes_text.endswith("'")) or \
           (notes_text.startswith('"') and notes_text.endswith('"')):
            notes_text = notes_text[1:-1]

        if not notes_text.strip():
            print("Error: Meeting notes cannot be empty")
            return

        print("Processing meeting notes...")
        result = await self.agent.process_meeting_notes(notes_text)
        
        if result.get("success"):
            data = result.get("data", {})
            action_items = data.get("action_items", [])
            delegation_result = data.get("delegation_result", {})
            
            if action_items:
                print(f"\n✓ Found {len(action_items)} action items:")
                for i, item in enumerate(action_items, 1):
                    print(f"  {i}. {item}")
                
                if delegation_result:
                    successful = delegation_result.get("successful_delegations", 0)
                    failed = delegation_result.get("failed_delegations", 0)
                    print(f"\n✓ Successfully delegated {successful} tasks")
                    if failed > 0:
                        print(f"✗ Failed to delegate {failed} tasks")
            else:
                print("No action items found in the meeting notes.")
        else:
            print(f"✗ {result.get('message')}")

    async def handle_process_file(self, args: list) -> None:
        """Handle the process file command."""
        if not args:
            print("Error: File path is required")
            print("Usage: process file <filepath>")
            return

        if len(args) > 1:
            print("Warning: Only the first argument will be used as file path")

        file_path = args[0]
        print(f"Processing file: {file_path}")
        
        result = await self.agent.process_meeting_file(file_path)
        
        if result.get("success"):
            data = result.get("data", {})
            action_items = data.get("action_items", [])
            delegation_result = data.get("delegation_result", {})
            
            if action_items:
                print(f"\n✓ Found {len(action_items)} action items:")
                for i, item in enumerate(action_items, 1):
                    print(f"  {i}. {item}")
                
                if delegation_result:
                    successful = delegation_result.get("successful_delegations", 0)
                    failed = delegation_result.get("failed_delegations", 0)
                    print(f"\n✓ Successfully delegated {successful} tasks")
                    if failed > 0:
                        print(f"✗ Failed to delegate {failed} tasks")
            else:
                print("No action items found in the file.")
        else:
            print(f"✗ {result.get('message')}")

    async def handle_extract_action_items(self, args: list) -> None:
        """Handle the extract command (extract without delegating)."""
        if not args:
            print("Error: Text is required")
            print("Usage: extract 'Text to extract action items from'")
            return

        # Join all arguments as the text
        text = " ".join(args)
        
        # Remove quotes if present
        if (text.startswith("'") and text.endswith("'")) or \
           (text.startswith('"') and text.endswith('"')):
            text = text[1:-1]

        if not text.strip():
            print("Error: Text cannot be empty")
            return

        print("Extracting action items...")
        action_items = self.agent.extract_action_items(text)
        
        if action_items:
            print(f"\n✓ Found {len(action_items)} action items:")
            for i, item in enumerate(action_items, 1):
                print(f"  {i}. {item}")
        else:
            print("No action items found in the text.")

    def handle_show_keywords(self, args: list) -> None:
        """Handle the keywords command."""
        if args:
            print("Warning: 'keywords' command doesn't take arguments")
        
        keywords = self.agent.task_keywords
        print(f"\nSupported action item keywords ({len(keywords)}):")
        for i, keyword in enumerate(keywords, 1):
            print(f"  {i}. {keyword}")

    def handle_add_keyword(self, args: list) -> None:
        """Handle the add keyword command."""
        if not args:
            print("Error: Keyword is required")
            print("Usage: add keyword <keyword>")
            return

        if len(args) > 1:
            print("Warning: Only the first argument will be used as keyword")

        keyword = args[0]
        result = self.agent.add_custom_keyword(keyword)
        
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ {result.get('message')}")

    def handle_remove_keyword(self, args: list) -> None:
        """Handle the remove keyword command."""
        if not args:
            print("Error: Keyword is required")
            print("Usage: remove keyword <keyword>")
            return

        if len(args) > 1:
            print("Warning: Only the first argument will be used as keyword")

        keyword = args[0]
        result = self.agent.remove_custom_keyword(keyword)
        
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ {result.get('message')}")

    def handle_capabilities(self, args: list) -> None:
        """Handle the capabilities command."""
        if args:
            print("Warning: 'capabilities' command doesn't take arguments")
        
        result = self.agent.get_capabilities()
        if result.get("success"):
            data = result.get("data", {})
            print(f"\nAgent: {data.get('agent_name')}")
            print(f"Capabilities: {', '.join(data.get('capabilities', []))}")
            print(f"Supported file formats: {', '.join(data.get('supported_file_formats', []))}")
        else:
            print(f"✗ {result.get('message')}")

    async def handle_health_check(self, args: list) -> None:
        """Handle the health check command."""
        if args:
            print("Warning: 'health' command doesn't take arguments")
        
        result = await self.agent.health_check()
        if result.get("success"):
            print(f"✓ {result.get('message')}")
        else:
            print(f"✗ {result.get('message')}")

    async def process_command(self, command: str) -> bool:
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
        elif cmd == "process" and args and args[0] == "notes":
            await self.handle_process_notes(args[1:])
        elif cmd == "process" and args and args[0] == "file":
            await self.handle_process_file(args[1:])
        elif cmd == "extract":
            await self.handle_extract_action_items(args)
        elif cmd == "keywords":
            self.handle_show_keywords(args)
        elif cmd == "add" and args and args[0] == "keyword":
            self.handle_add_keyword(args[1:])
        elif cmd == "remove" and args and args[0] == "keyword":
            self.handle_remove_keyword(args[1:])
        elif cmd == "capabilities":
            self.handle_capabilities(args)
        elif cmd == "health":
            await self.handle_health_check(args)
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")

        return True

    async def run(self) -> None:
        """Run the CLI application."""
        print("=" * 60)
        print("Meeting Assistant Agent")
        print("=" * 60)
        print("Type 'help' for available commands")
        print("Type 'quit' to exit")
        print()

        self.running = True
        while self.running:
            try:
                command = input("Meeting Assistant Agent> ").strip()
                if not await self.process_command(command):
                    break
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit gracefully")
            except EOFError:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")


async def main():
    """Main function to run the Meeting Assistant CLI."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    cli = MeetingAssistantCLI()
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main()) 