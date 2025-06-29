#!/usr/bin/env python3
"""Simple script to start the A2A server."""

import asyncio
import threading
from protocols.a2a_server import A2AServer
from agents.task_manager_agent import TaskManagerAgent

def start_a2a_server():
    """Start the A2A server with proper handlers."""
    # Create task manager agent to get the handlers
    agent = TaskManagerAgent()
    
    # Start the A2A server
    print("Starting A2A server...")
    agent.start_a2a_server()

if __name__ == "__main__":
    start_a2a_server() 