"""
Cohere AI Agent for Task Management.
Phase III: AI Chatbot - Conversational agent using Cohere FREE API

This module provides the AI agent that:
- Uses Cohere API (FREE tier, command-r model)
- Parses user intent with lightweight NLP
- Executes task operations via MCP-style tools
- Provides conversational, friendly responses
- Works in DEMO MODE when API key is missing
"""
import json
import re
import httpx
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from ..config import get_settings


# System prompt for task-related responses
SYSTEM_PROMPT = """You are PakAura Assistant, a friendly and helpful task management assistant.

Your personality:
- Be warm, conversational, and encouraging
- Use emojis sparingly but appropriately
- Keep responses brief (2-4 sentences)
- Celebrate user accomplishments
- Be helpful and proactive

When responding:
- Confirm actions clearly
- Format task lists nicely with bullet points
- Ask for clarification if the request is unclear
- Stay focused on task management

Examples:
- "I've added 'Buy groceries' to your list! You now have 5 tasks."
- "Great job completing that task! Only 3 left to go."
- "Here are your tasks:\n• Buy groceries\n• Call mom\n• Finish report"
"""

# System prompt for general conversation (non-task questions)
CHAT_SYSTEM_PROMPT = """You are PakAura Assistant, a friendly and knowledgeable AI assistant.

Your personality:
- Be warm, helpful, and conversational
- Keep responses concise (2-4 sentences unless more detail is needed)
- Be informative and accurate
- Use a friendly, human tone

Guidelines:
- Answer questions naturally and directly
- Provide helpful information on any topic
- Be polite and engaging
- Do NOT mention tasks unless the user asks about them
- Do NOT offer to help with tasks unless relevant

Examples:
- User: "how are you" → "I'm doing great, thank you for asking! How can I help you today?"
- User: "what is AI" → "AI (Artificial Intelligence) is technology that enables machines to learn and make decisions like humans. It powers everything from voice assistants to recommendation systems!"
"""


@dataclass
class AgentResult:
    """Result from agent processing."""
    response: str
    tool_calls: List[Dict[str, Any]]
    conversation_id: Optional[str] = None


class CohereTaskAgent:
    """
    AI Agent for task management using Cohere API.

    Uses Cohere's command-r model (FREE tier) for natural language understanding
    and response generation. Includes intent detection and tool execution.
    """

    COHERE_API_URL = "https://api.cohere.com/v2/chat"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Cohere task agent.

        Args:
            api_key: Cohere API key (defaults to settings)
        """
        settings = get_settings()
        self.api_key = api_key or settings.cohere_api_key
        self.model = settings.ai_model
        self.max_tokens = settings.ai_max_tokens
        self.temperature = settings.ai_temperature
        self.timeout = settings.ai_timeout_seconds

        self.task_ops = None
        self._initialized = False
        self._demo_mode = not self.api_key

    @property
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (no API key)."""
        return self._demo_mode

    async def initialize(self, database_url: Optional[str] = None):
        """
        Initialize the agent and database connection.

        Args:
            database_url: Database URL for task operations
        """
        if self._initialized:
            return

        from ..mcp_server.task_operations import TaskOperations

        settings = get_settings()
        db_url = database_url or settings.database_url

        self.task_ops = TaskOperations(database_url=db_url)
        self._initialized = True

    def _detect_intent(self, message: str) -> tuple[str, dict]:
        """
        Detect user intent using lightweight keyword NLP.

        Args:
            message: User's message

        Returns:
            Tuple of (intent, extracted_data)
        """
        msg_lower = message.lower().strip()

        # Greeting detection (must be at start or standalone)
        greetings = ["hello", "hey", "good morning", "good afternoon",
                     "good evening", "howdy", "greetings", "what's up", "sup"]
        # Check for "hi" separately to avoid matching "this", "within", etc.
        if msg_lower in ["hi", "hi!"] or msg_lower.startswith("hi ") or msg_lower.startswith("hi!"):
            return "greeting", {}
        if any(msg_lower.startswith(greet) or msg_lower == greet for greet in greetings):
            return "greeting", {}

        # Help detection
        help_words = ["help", "what can you do", "how do i", "how to", "assist"]
        if any(word in msg_lower for word in help_words):
            return "help", {}

        # Add task detection
        add_patterns = ["add", "create", "new task", "remember", "make a task"]
        if any(pattern in msg_lower for pattern in add_patterns):
            # Extract task title
            title = self._extract_task_title(message, add_patterns)
            return "add_task", {"title": title}

        # List tasks detection
        list_patterns = ["list", "show", "view", "see", "my tasks", "all tasks",
                        "what are my", "display", "get tasks"]
        if any(pattern in msg_lower for pattern in list_patterns):
            # Check for filter
            filter_type = "all"
            if "completed" in msg_lower or "done" in msg_lower or "finished" in msg_lower:
                filter_type = "completed"
            elif "incomplete" in msg_lower or "pending" in msg_lower or "not done" in msg_lower:
                filter_type = "incomplete"
            return "list_tasks", {"filter": filter_type}

        # Clear completed tasks detection (check before delete/complete)
        clear_patterns = ["clear completed", "remove completed", "delete completed",
                         "clear done", "remove done", "delete done", "clean up"]
        if any(pattern in msg_lower for pattern in clear_patterns):
            return "clear_completed", {}

        # Delete task detection (check before complete to handle "remove" properly)
        delete_patterns = ["delete", "remove", "get rid of", "erase", "trash"]
        if any(pattern in msg_lower for pattern in delete_patterns):
            task_ref = self._extract_task_reference(message)
            return "delete_task", {"task_ref": task_ref}

        # Uncomplete task detection (check before complete)
        uncomplete_patterns = ["uncomplete", "mark as incomplete", "mark incomplete",
                              "mark as not done", "undo complete", "uncheck",
                              "mark as undone", "reopen"]
        if any(pattern in msg_lower for pattern in uncomplete_patterns):
            task_ref = self._extract_task_reference(message)
            return "uncomplete_task", {"task_ref": task_ref}

        # Complete task detection
        complete_patterns = ["complete", "mark as done", "finish", "done with",
                           "mark complete", "i finished", "i completed", "check off"]
        if any(pattern in msg_lower for pattern in complete_patterns):
            task_ref = self._extract_task_reference(message)
            return "complete_task", {"task_ref": task_ref}

        # Update task detection
        update_patterns = ["update", "change", "modify", "rename", "edit"]
        if any(pattern in msg_lower for pattern in update_patterns):
            task_ref = self._extract_task_reference(message)
            new_title = self._extract_new_title(message)
            return "update_task", {"task_ref": task_ref, "new_title": new_title}

        # Unknown intent
        return "unknown", {}

    def _extract_task_title(self, message: str, patterns: list) -> str:
        """Extract task title from message."""
        msg = message
        for pattern in patterns:
            if pattern in message.lower():
                # Find the pattern and get text after it
                idx = message.lower().find(pattern)
                msg = message[idx + len(pattern):].strip()
                break

        # Clean up common prefixes
        prefixes = ["task", "a task", "task:", ":", "to", "called", "named"]
        for prefix in prefixes:
            if msg.lower().startswith(prefix):
                msg = msg[len(prefix):].strip()

        # Clean up quotes
        msg = msg.strip('"\'')

        return msg.strip() if msg else message

    def _extract_task_reference(self, message: str) -> str:
        """Extract task reference (title or ID) from message."""
        # Look for quoted text first
        quoted = re.findall(r'["\']([^"\']+)["\']', message)
        if quoted:
            return quoted[0]

        # Try to extract after common patterns
        patterns = ["task", "the task", "called", "named", "titled"]
        msg_lower = message.lower()
        for pattern in patterns:
            if pattern in msg_lower:
                idx = msg_lower.find(pattern) + len(pattern)
                ref = message[idx:].strip()
                # Take first few words
                words = ref.split()[:5]
                return " ".join(words).strip('.,!?')

        return message

    def _extract_new_title(self, message: str) -> str:
        """Extract new title from update message."""
        patterns = ["to", "with", "as", "new title"]
        msg_lower = message.lower()
        for pattern in patterns:
            if pattern in msg_lower:
                idx = msg_lower.rfind(pattern) + len(pattern)
                return message[idx:].strip().strip('"\'')
        return ""

    def _is_meaningless(self, message: str) -> bool:
        """
        Check if message is empty or meaningless (gibberish).

        Returns True for:
        - Empty strings
        - Only whitespace
        - Single characters
        - Random keyboard mashing (e.g., "asdfgh")
        - Only punctuation
        """
        msg = message.strip()

        # Empty or very short
        if not msg or len(msg) < 2:
            return True

        # Only punctuation or symbols (no letters/numbers)
        if not any(c.isalnum() for c in msg):
            return True

        # Single repeated character (e.g., "aaaaaa", "???")
        unique_chars = set(msg.lower().replace(" ", ""))
        if len(unique_chars) <= 2 and len(msg) > 3:
            return True

        return False

    async def _call_cohere(self, messages: List[Dict], user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Call Cohere API for response generation.

        Args:
            messages: Conversation history
            user_message: Current user message
            system_prompt: Optional custom system prompt (defaults to SYSTEM_PROMPT)

        Returns:
            Generated response text
        """
        if self._demo_mode:
            return ""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        # Build message history for Cohere v2
        cohere_messages = [
            {"role": "system", "content": system_prompt or SYSTEM_PROMPT}
        ]

        # Add conversation history (last 10 messages for context)
        for msg in messages[-10:]:
            if msg.get("role") in ["user", "assistant"]:
                cohere_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Add current message
        cohere_messages.append({
            "role": "user",
            "content": user_message
        })

        payload = {
            "model": self.model,
            "messages": cohere_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.COHERE_API_URL,
                    headers=headers,
                    json=payload
                )

                if response.status_code == 429:
                    raise Exception("Rate limit exceeded")

                if response.status_code >= 400:
                    raise Exception(f"API error: {response.status_code}")

                data = response.json()

                # Extract text from Cohere v2 response
                message = data.get("message", {})
                content = message.get("content", [])

                for block in content:
                    if block.get("type") == "text":
                        return block.get("text", "")

                return ""

        except httpx.TimeoutException:
            raise Exception("Request timed out")
        except Exception as e:
            raise

    async def _find_task_by_reference(self, user_id: str, ref: str) -> Optional[Dict]:
        """Find a task by title reference."""
        if not self.task_ops:
            return None

        result = await self.task_ops.list_tasks(user_id, "all")
        if not result.get("success"):
            return None

        tasks = result.get("tasks", [])
        ref_lower = ref.lower().strip()

        # Exact match first
        for task in tasks:
            if task["title"].lower() == ref_lower:
                return task

        # Partial match
        for task in tasks:
            if ref_lower in task["title"].lower():
                return task

        # Word match
        ref_words = set(ref_lower.split())
        for task in tasks:
            title_words = set(task["title"].lower().split())
            if ref_words & title_words:  # Intersection
                return task

        return None

    def _format_task_list(self, tasks: List[Dict]) -> str:
        """Format tasks as a nice bullet list."""
        if not tasks:
            return "You don't have any tasks yet. Would you like to add one?"

        lines = []
        for task in tasks:
            status = "✅" if task.get("completed") else "⬜"
            lines.append(f"• {status} {task['title']}")

        return "\n".join(lines)

    def _get_demo_response(self, intent: str, data: dict) -> AgentResult:
        """Generate demo mode responses."""
        responses = {
            "greeting": "Hello! I'm PakAura Assistant running in Demo Mode. I can help you manage tasks. Try 'show my tasks' or 'add task buy groceries'!",
            "help": "I'm your task management assistant! Here's what I can do:\n• **Show tasks**: 'show my tasks'\n• **Add tasks**: 'add task [name]'\n• **Complete tasks**: 'complete [task name]'\n• **Uncomplete tasks**: 'uncomplete [task name]'\n• **Delete tasks**: 'delete [task name]'\n• **Clear completed**: 'clear completed tasks'\n\nJust tell me what you'd like to do!",
            "add_task": f"I'll add '{data.get('title', 'your task')}' to your list!",
            "list_tasks": "Let me show you your tasks...",
            "complete_task": f"I'll mark that task as complete!",
            "uncomplete_task": f"I'll mark that task as incomplete!",
            "delete_task": f"I'll delete that task for you!",
            "clear_completed": "I'll clear all your completed tasks!",
            "update_task": "To update tasks in Demo Mode, please use the task list UI. Add a Cohere API key for voice commands!",
            "unknown": "I'm not sure what you'd like to do. Try:\n• 'show my tasks'\n• 'add task [name]'\n• 'complete [task name]'\n• 'delete [task name]'\n• 'help'"
        }

        return AgentResult(
            response=responses.get(intent, responses["unknown"]),
            tool_calls=[]
        )

    async def chat(
        self,
        user_id: str,
        message: str,
        history: Optional[List[Dict[str, Any]]] = None
    ) -> AgentResult:
        """
        Process a user message and return agent response.

        Args:
            user_id: UUID of the user
            message: User's message
            history: Previous conversation messages

        Returns:
            AgentResult with response and tool calls
        """
        if not self._initialized:
            await self.initialize()

        history = history or []
        tool_calls = []

        # Detect intent
        intent, data = self._detect_intent(message)

        # Handle greeting
        if intent == "greeting":
            if self._demo_mode:
                return self._get_demo_response(intent, data)

            try:
                ai_response = await self._call_cohere(history, message)
                if ai_response:
                    return AgentResult(response=ai_response, tool_calls=[])
            except:
                pass

            return AgentResult(
                response="Hello! I'm PakAura Assistant. How can I help you with your tasks today?",
                tool_calls=[]
            )

        # Handle help
        if intent == "help":
            return AgentResult(
                response="I can help you manage your tasks! Here's what I can do:\n• **Add tasks**: 'add task buy groceries'\n• **Show tasks**: 'show my tasks'\n• **Complete tasks**: 'complete buy groceries'\n• **Delete tasks**: 'delete buy groceries'\n• **Update tasks**: 'update buy groceries to buy organic groceries'\n\nJust tell me what you'd like to do!",
                tool_calls=[]
            )

        # Handle add task
        if intent == "add_task":
            title = data.get("title", "").strip()
            if not title:
                return AgentResult(
                    response="What would you like to name your new task?",
                    tool_calls=[]
                )

            result = await self.task_ops.add_task(user_id, title)
            tool_calls.append({"tool": "add_task", "result": result})

            if result.get("success"):
                task = result.get("task", {})
                response = f"I've added '{task.get('title', title)}' to your task list!"

                # Get AI enhancement if available
                if not self._demo_mode:
                    try:
                        ai_response = await self._call_cohere(
                            history,
                            f"The user asked to add a task called '{title}' and it was successful. Give a brief, friendly confirmation."
                        )
                        if ai_response:
                            response = ai_response
                    except:
                        pass

                return AgentResult(response=response, tool_calls=tool_calls)
            else:
                return AgentResult(
                    response=f"Sorry, I couldn't add that task: {result.get('error', 'Unknown error')}",
                    tool_calls=tool_calls
                )

        # Handle list tasks
        if intent == "list_tasks":
            filter_type = data.get("filter", "all")
            result = await self.task_ops.list_tasks(user_id, filter_type)
            tool_calls.append({"tool": "list_tasks", "result": result})

            if result.get("success"):
                tasks = result.get("tasks", [])
                task_list = self._format_task_list(tasks)

                if not tasks:
                    response = "You don't have any tasks yet. Would you like to add one? Just say 'add task [name]'!"
                else:
                    count = len(tasks)
                    completed = sum(1 for t in tasks if t.get("completed"))
                    response = f"Here are your tasks ({completed}/{count} completed):\n\n{task_list}"

                return AgentResult(response=response, tool_calls=tool_calls)
            else:
                return AgentResult(
                    response="Sorry, I couldn't retrieve your tasks. Please try again.",
                    tool_calls=tool_calls
                )

        # Handle complete task
        if intent == "complete_task":
            task_ref = data.get("task_ref", "").strip()
            if not task_ref:
                return AgentResult(
                    response="Which task would you like to mark as complete?",
                    tool_calls=[]
                )

            # Find the task
            task = await self._find_task_by_reference(user_id, task_ref)
            if not task:
                # List available tasks
                result = await self.task_ops.list_tasks(user_id, "incomplete")
                tasks = result.get("tasks", [])
                if tasks:
                    task_list = self._format_task_list(tasks)
                    return AgentResult(
                        response=f"I couldn't find a task matching '{task_ref}'. Here are your pending tasks:\n\n{task_list}\n\nWhich one would you like to complete?",
                        tool_calls=[]
                    )
                return AgentResult(
                    response=f"I couldn't find a task matching '{task_ref}'. You don't have any pending tasks!",
                    tool_calls=[]
                )

            result = await self.task_ops.complete_task(user_id, task["id"])
            tool_calls.append({"tool": "complete_task", "result": result})

            if result.get("success"):
                response = f"Great job! I've marked '{task['title']}' as complete! Keep up the good work!"
                return AgentResult(response=response, tool_calls=tool_calls)
            else:
                return AgentResult(
                    response=f"Sorry, I couldn't complete that task: {result.get('error', 'Unknown error')}",
                    tool_calls=tool_calls
                )

        # Handle delete task
        if intent == "delete_task":
            task_ref = data.get("task_ref", "").strip()
            if not task_ref:
                return AgentResult(
                    response="Which task would you like to delete?",
                    tool_calls=[]
                )

            task = await self._find_task_by_reference(user_id, task_ref)
            if not task:
                result = await self.task_ops.list_tasks(user_id, "all")
                tasks = result.get("tasks", [])
                if tasks:
                    task_list = self._format_task_list(tasks)
                    return AgentResult(
                        response=f"I couldn't find a task matching '{task_ref}'. Here are your tasks:\n\n{task_list}\n\nWhich one would you like to delete?",
                        tool_calls=[]
                    )
                return AgentResult(
                    response="You don't have any tasks to delete!",
                    tool_calls=[]
                )

            result = await self.task_ops.delete_task(user_id, task["id"])
            tool_calls.append({"tool": "delete_task", "result": result})

            if result.get("success"):
                return AgentResult(
                    response=f"Done! I've removed '{task['title']}' from your list.",
                    tool_calls=tool_calls
                )
            else:
                return AgentResult(
                    response=f"Sorry, I couldn't delete that task: {result.get('error', 'Unknown error')}",
                    tool_calls=tool_calls
                )

        # Handle uncomplete task
        if intent == "uncomplete_task":
            task_ref = data.get("task_ref", "").strip()
            if not task_ref:
                return AgentResult(
                    response="Which task would you like to mark as incomplete?",
                    tool_calls=[]
                )

            # Find the task
            task = await self._find_task_by_reference(user_id, task_ref)
            if not task:
                result = await self.task_ops.list_tasks(user_id, "completed")
                tasks = result.get("tasks", [])
                if tasks:
                    task_list = self._format_task_list(tasks)
                    return AgentResult(
                        response=f"I couldn't find a task matching '{task_ref}'. Here are your completed tasks:\n\n{task_list}\n\nWhich one would you like to uncomplete?",
                        tool_calls=[]
                    )
                return AgentResult(
                    response=f"I couldn't find a task matching '{task_ref}'. You don't have any completed tasks!",
                    tool_calls=[]
                )

            result = await self.task_ops.uncomplete_task(user_id, task["id"])
            tool_calls.append({"tool": "uncomplete_task", "result": result})

            if result.get("success"):
                response = f"Done! I've marked '{task['title']}' as incomplete. Back on the to-do list!"
                return AgentResult(response=response, tool_calls=tool_calls)
            else:
                return AgentResult(
                    response=f"Sorry, I couldn't uncomplete that task: {result.get('error', 'Unknown error')}",
                    tool_calls=tool_calls
                )

        # Handle clear completed tasks
        if intent == "clear_completed":
            result = await self.task_ops.clear_completed(user_id)
            tool_calls.append({"tool": "clear_completed", "result": result})

            if result.get("success"):
                count = result.get("deleted_count", 0)
                if count == 0:
                    return AgentResult(
                        response="You don't have any completed tasks to clear!",
                        tool_calls=tool_calls
                    )
                return AgentResult(
                    response=f"Done! I've cleared {count} completed task{'s' if count != 1 else ''}. Your list is looking cleaner!",
                    tool_calls=tool_calls
                )
            else:
                return AgentResult(
                    response=f"Sorry, I couldn't clear completed tasks: {result.get('error', 'Unknown error')}",
                    tool_calls=tool_calls
                )

        # Handle update task
        if intent == "update_task":
            task_ref = data.get("task_ref", "").strip()
            new_title = data.get("new_title", "").strip()

            if not task_ref:
                return AgentResult(
                    response="Which task would you like to update?",
                    tool_calls=[]
                )

            task = await self._find_task_by_reference(user_id, task_ref)
            if not task:
                result = await self.task_ops.list_tasks(user_id, "all")
                tasks = result.get("tasks", [])
                if tasks:
                    task_list = self._format_task_list(tasks)
                    return AgentResult(
                        response=f"I couldn't find a task matching '{task_ref}'. Here are your tasks:\n\n{task_list}\n\nWhich one would you like to update?",
                        tool_calls=[]
                    )
                return AgentResult(
                    response="You don't have any tasks to update!",
                    tool_calls=[]
                )

            if not new_title:
                return AgentResult(
                    response=f"What would you like to rename '{task['title']}' to?",
                    tool_calls=[]
                )

            result = await self.task_ops.update_task(user_id, task["id"], new_title)
            tool_calls.append({"tool": "update_task", "result": result})

            if result.get("success"):
                return AgentResult(
                    response=f"Done! I've updated '{task['title']}' to '{new_title}'.",
                    tool_calls=tool_calls
                )
            else:
                return AgentResult(
                    response=f"Sorry, I couldn't update that task: {result.get('error', 'Unknown error')}",
                    tool_calls=tool_calls
                )

        # Unknown intent - handle as general conversation or help

        # Only show help if message is truly meaningless/empty
        if self._is_meaningless(message):
            return AgentResult(
                response="I'm not quite sure what you'd like to do. I can help you:\n• **Add tasks**: 'add task [name]'\n• **Show tasks**: 'show my tasks'\n• **Complete tasks**: 'complete [task name]'\n• **Delete tasks**: 'delete [task name]'\n\nWhat would you like to do?",
                tool_calls=[]
            )

        # For meaningful non-task messages, use Cohere for general conversation
        if not self._demo_mode:
            try:
                ai_response = await self._call_cohere(
                    history,
                    message,
                    system_prompt=CHAT_SYSTEM_PROMPT
                )
                if ai_response:
                    return AgentResult(response=ai_response, tool_calls=[])
            except Exception as e:
                print(f"Cohere error: {e}")

        # Demo mode fallback for general conversation
        return AgentResult(
            response="I'd be happy to chat! While I'm best at helping with task management, feel free to ask me anything. For tasks, try 'show my tasks' or 'add task [name]'.",
            tool_calls=[]
        )

    async def cleanup(self):
        """Clean up resources."""
        self._initialized = False
        self.task_ops = None


# Aliases for backwards compatibility
TaskManagerAgent = CohereTaskAgent
SimplifiedTaskAgent = CohereTaskAgent


def get_agent(use_simplified: bool = True) -> CohereTaskAgent:
    """
    Get a task manager agent instance.

    Args:
        use_simplified: Ignored, always returns CohereTaskAgent

    Returns:
        CohereTaskAgent instance
    """
    return CohereTaskAgent()
