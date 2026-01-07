"""Main entry point for the Todo CLI application.

This module implements the REPL (Read-Eval-Print Loop) that serves
as the interactive command-line interface for managing tasks.
"""

import sys
from .services.task_service import TaskService
from .cli.commands import CommandHandler


def print_banner() -> None:
    """Display the application startup banner."""
    print("=" * 50)
    print("  Todo CLI Application")
    print("  Type 'help' for available commands")
    print("  Type 'exit' to quit")
    print("=" * 50)
    print()


def main() -> None:
    """Run the main REPL loop.

    Creates a TaskService and CommandHandler, then enters an infinite
    loop reading user input and executing commands until 'exit' is called
    or the user sends EOF (Ctrl+D) or interrupt (Ctrl+C).
    """
    # Initialize services
    task_service = TaskService()
    handler = CommandHandler(task_service)

    # Display startup banner
    print_banner()

    # REPL loop
    while True:
        try:
            # Read input with prompt
            user_input = input("todo> ")

            # Execute command
            response, should_exit = handler.execute(user_input)

            # Print response if not empty
            if response:
                print(response)
                print()  # Blank line for readability

            # Check if we should exit
            if should_exit:
                break

        except EOFError:
            # Handle Ctrl+D (EOF)
            print("\nGoodbye!")
            break

        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
