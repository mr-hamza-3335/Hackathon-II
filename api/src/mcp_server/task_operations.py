"""
Database operations for MCP tools.
Phase III: AI Chatbot - Stateless task operations (all state in PostgreSQL)

All operations are stateless and interact directly with PostgreSQL.
"""
import os
import asyncpg
from uuid import UUID
from typing import Optional


class TaskOperations:
    """
    Stateless database operations for task management.
    All state is persisted in PostgreSQL.
    """

    def __init__(self, database_url: Optional[str] = None):
        """Initialize with database URL from environment or parameter."""
        self.database_url = database_url or os.environ.get("DATABASE_URL", "")
        # Convert SQLAlchemy URL to asyncpg URL if needed
        if self.database_url.startswith("postgresql+asyncpg://"):
            self.database_url = self.database_url.replace("postgresql+asyncpg://", "postgresql://")

    async def get_connection(self):
        """Get a database connection."""
        return await asyncpg.connect(self.database_url)

    async def add_task(self, user_id: str, title: str) -> dict:
        """
        Create a new task for the user.

        Args:
            user_id: UUID of the user
            title: Task title (1-500 chars)

        Returns:
            dict with success status and task data or error
        """
        if not title or not title.strip():
            return {"success": False, "error": "Task title cannot be empty"}

        if len(title) > 500:
            return {"success": False, "error": "Task title cannot exceed 500 characters"}

        conn = await self.get_connection()
        try:
            # Verify user exists
            user = await conn.fetchrow(
                "SELECT id FROM users WHERE id = $1",
                UUID(user_id)
            )
            if not user:
                return {"success": False, "error": "User not found"}

            # Create task
            row = await conn.fetchrow(
                """
                INSERT INTO tasks (user_id, title, completed)
                VALUES ($1, $2, false)
                RETURNING id, title, completed, created_at
                """,
                UUID(user_id),
                title.strip()
            )

            return {
                "success": True,
                "task": {
                    "id": str(row["id"]),
                    "title": row["title"],
                    "completed": row["completed"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await conn.close()

    async def list_tasks(self, user_id: str, filter: str = "all") -> dict:
        """
        List tasks for a user with optional filter.

        Args:
            user_id: UUID of the user
            filter: 'all', 'completed', or 'incomplete'

        Returns:
            dict with success status, tasks list, and count
        """
        conn = await self.get_connection()
        try:
            # Build query based on filter
            base_query = "SELECT id, title, completed, created_at FROM tasks WHERE user_id = $1"

            if filter == "completed":
                query = base_query + " AND completed = true ORDER BY created_at DESC"
            elif filter == "incomplete":
                query = base_query + " AND completed = false ORDER BY created_at DESC"
            else:  # all
                query = base_query + " ORDER BY created_at DESC"

            rows = await conn.fetch(query, UUID(user_id))

            tasks = [
                {
                    "id": str(row["id"]),
                    "title": row["title"],
                    "completed": row["completed"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                }
                for row in rows
            ]

            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks),
                "filter": filter
            }
        except Exception as e:
            return {"success": False, "error": str(e), "tasks": [], "count": 0}
        finally:
            await conn.close()

    async def complete_task(self, user_id: str, task_id: str) -> dict:
        """
        Mark a task as completed.

        Args:
            user_id: UUID of the user (for authorization)
            task_id: UUID of the task

        Returns:
            dict with success status and updated task data
        """
        conn = await self.get_connection()
        try:
            # Update task only if it belongs to the user
            row = await conn.fetchrow(
                """
                UPDATE tasks
                SET completed = true, updated_at = now()
                WHERE id = $1 AND user_id = $2
                RETURNING id, title, completed, updated_at
                """,
                UUID(task_id),
                UUID(user_id)
            )

            if not row:
                return {
                    "success": False,
                    "error": "Task not found or you don't have permission to update it"
                }

            return {
                "success": True,
                "task": {
                    "id": str(row["id"]),
                    "title": row["title"],
                    "completed": row["completed"],
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await conn.close()

    async def delete_task(self, user_id: str, task_id: str) -> dict:
        """
        Delete a task permanently.

        Args:
            user_id: UUID of the user (for authorization)
            task_id: UUID of the task

        Returns:
            dict with success status and deleted task info
        """
        conn = await self.get_connection()
        try:
            # Get task info before deletion (for confirmation message)
            task = await conn.fetchrow(
                "SELECT id, title FROM tasks WHERE id = $1 AND user_id = $2",
                UUID(task_id),
                UUID(user_id)
            )

            if not task:
                return {
                    "success": False,
                    "error": "Task not found or you don't have permission to delete it"
                }

            # Delete the task
            await conn.execute(
                "DELETE FROM tasks WHERE id = $1 AND user_id = $2",
                UUID(task_id),
                UUID(user_id)
            )

            return {
                "success": True,
                "deleted": True,
                "deleted_id": str(task["id"]),
                "deleted_title": task["title"]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await conn.close()

    async def update_task(self, user_id: str, task_id: str, title: str) -> dict:
        """
        Update a task's title.

        Args:
            user_id: UUID of the user (for authorization)
            task_id: UUID of the task
            title: New task title (1-500 chars)

        Returns:
            dict with success status and updated task data
        """
        if not title or not title.strip():
            return {"success": False, "error": "Task title cannot be empty"}

        if len(title) > 500:
            return {"success": False, "error": "Task title cannot exceed 500 characters"}

        conn = await self.get_connection()
        try:
            row = await conn.fetchrow(
                """
                UPDATE tasks
                SET title = $1, updated_at = now()
                WHERE id = $2 AND user_id = $3
                RETURNING id, title, completed, updated_at
                """,
                title.strip(),
                UUID(task_id),
                UUID(user_id)
            )

            if not row:
                return {
                    "success": False,
                    "error": "Task not found or you don't have permission to update it"
                }

            return {
                "success": True,
                "task": {
                    "id": str(row["id"]),
                    "title": row["title"],
                    "completed": row["completed"],
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            await conn.close()
