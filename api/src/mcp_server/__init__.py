"""
MCP Server for Task Management.
Phase III: AI Chatbot - Model Context Protocol Server

This MCP Server exposes task management tools:
- add_task: Create a new task
- list_tasks: List user's tasks
- complete_task: Mark task as done
- delete_task: Remove a task
- update_task: Update task title

All tools are stateless - state persisted in PostgreSQL.
"""
from .server import create_server, run_server
from .tools import TaskTools
from .task_operations import TaskOperations

__all__ = ["create_server", "run_server", "TaskTools", "TaskOperations"]
