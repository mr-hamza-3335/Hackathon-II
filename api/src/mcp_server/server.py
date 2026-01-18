"""
MCP Server for Task Management.
Phase III: AI Chatbot - Model Context Protocol Server

This server exposes task management tools via the MCP protocol.
It can be run as a standalone process or spawned by the FastAPI backend.

Usage:
    python -m api.src.mcp_server.server

The server communicates via stdio and expects DATABASE_URL environment variable.
"""
import asyncio
import os
import sys
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server

from .task_operations import TaskOperations
from .tools import TaskTools


def create_server(database_url: Optional[str] = None) -> Server:
    """
    Create and configure the MCP server.

    Args:
        database_url: Database connection URL (defaults to DATABASE_URL env var)

    Returns:
        Configured MCP Server instance
    """
    # Initialize server
    server = Server("task-manager")

    # Initialize task operations with database connection
    operations = TaskOperations(database_url=database_url)

    # Register tools
    tools = TaskTools(operations)
    tools.register(server)

    return server


async def run_server(database_url: Optional[str] = None):
    """
    Run the MCP server.

    Args:
        database_url: Database connection URL (defaults to DATABASE_URL env var)
    """
    server = create_server(database_url)

    # Run server with stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Main entry point for the MCP server."""
    # Load database URL from environment
    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL environment variable is required", file=sys.stderr)
        sys.exit(1)

    # Run the server
    asyncio.run(run_server(database_url))


if __name__ == "__main__":
    main()
