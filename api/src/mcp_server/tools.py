"""
MCP Tool definitions for Task Management.
Phase III: AI Chatbot - Tool definitions using Official MCP SDK
"""
import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from .task_operations import TaskOperations


# Tool input schemas
ADD_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "description": "UUID of the user who owns the task"
        },
        "title": {
            "type": "string",
            "description": "Title of the task (1-500 characters)"
        }
    },
    "required": ["user_id", "title"]
}

LIST_TASKS_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "description": "UUID of the user whose tasks to list"
        },
        "filter": {
            "type": "string",
            "enum": ["all", "completed", "incomplete"],
            "description": "Filter tasks by completion status",
            "default": "all"
        }
    },
    "required": ["user_id"]
}

COMPLETE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "description": "UUID of the user (for authorization)"
        },
        "task_id": {
            "type": "string",
            "description": "UUID of the task to mark as complete"
        }
    },
    "required": ["user_id", "task_id"]
}

DELETE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "description": "UUID of the user (for authorization)"
        },
        "task_id": {
            "type": "string",
            "description": "UUID of the task to delete"
        }
    },
    "required": ["user_id", "task_id"]
}

UPDATE_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {
            "type": "string",
            "description": "UUID of the user (for authorization)"
        },
        "task_id": {
            "type": "string",
            "description": "UUID of the task to update"
        },
        "title": {
            "type": "string",
            "description": "New title for the task (1-500 characters)"
        }
    },
    "required": ["user_id", "task_id", "title"]
}


class TaskTools:
    """
    MCP Tools for task management.
    Registers tools with the MCP server.
    """

    def __init__(self, operations: TaskOperations):
        """
        Initialize with task operations handler.

        Args:
            operations: TaskOperations instance for database access
        """
        self.operations = operations

    def register(self, server: Server):
        """
        Register all task management tools with the MCP server.

        Args:
            server: MCP Server instance
        """

        @server.list_tools()
        async def list_tools() -> list[Tool]:
            """Return list of available tools."""
            return [
                Tool(
                    name="add_task",
                    description="Create a new task for the user. Use this when the user wants to add a new item to their task list.",
                    inputSchema=ADD_TASK_SCHEMA
                ),
                Tool(
                    name="list_tasks",
                    description="List all tasks for a user. Can filter by completion status (all, completed, incomplete). Use this when the user wants to see their tasks.",
                    inputSchema=LIST_TASKS_SCHEMA
                ),
                Tool(
                    name="complete_task",
                    description="Mark a task as completed. Use this when the user indicates they've finished a task.",
                    inputSchema=COMPLETE_TASK_SCHEMA
                ),
                Tool(
                    name="delete_task",
                    description="Delete a task permanently. Use this when the user wants to remove a task from their list.",
                    inputSchema=DELETE_TASK_SCHEMA
                ),
                Tool(
                    name="update_task",
                    description="Update a task's title. Use this when the user wants to change the description of an existing task.",
                    inputSchema=UPDATE_TASK_SCHEMA
                )
            ]

        @server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
            """
            Handle tool calls from the agent.

            Args:
                name: Tool name to call
                arguments: Tool arguments

            Returns:
                List of TextContent with JSON result
            """
            try:
                if name == "add_task":
                    result = await self.operations.add_task(
                        user_id=arguments["user_id"],
                        title=arguments["title"]
                    )
                elif name == "list_tasks":
                    result = await self.operations.list_tasks(
                        user_id=arguments["user_id"],
                        filter=arguments.get("filter", "all")
                    )
                elif name == "complete_task":
                    result = await self.operations.complete_task(
                        user_id=arguments["user_id"],
                        task_id=arguments["task_id"]
                    )
                elif name == "delete_task":
                    result = await self.operations.delete_task(
                        user_id=arguments["user_id"],
                        task_id=arguments["task_id"]
                    )
                elif name == "update_task":
                    result = await self.operations.update_task(
                        user_id=arguments["user_id"],
                        task_id=arguments["task_id"],
                        title=arguments["title"]
                    )
                else:
                    result = {"success": False, "error": f"Unknown tool: {name}"}

                return [TextContent(type="text", text=json.dumps(result))]

            except Exception as e:
                error_result = {"success": False, "error": str(e)}
                return [TextContent(type="text", text=json.dumps(error_result))]
