#!/usr/bin/env python3
"""
Quick import check script.
Run from api/ directory: python check_imports.py
"""

def check_imports():
    errors = []

    print("Checking imports...")

    # Check core dependencies
    try:
        import fastapi
        print(f"  ✓ fastapi {fastapi.__version__}")
    except ImportError as e:
        errors.append(f"  ✗ fastapi: {e}")

    try:
        import uvicorn
        print(f"  ✓ uvicorn")
    except ImportError as e:
        errors.append(f"  ✗ uvicorn: {e}")

    try:
        import pydantic
        print(f"  ✓ pydantic {pydantic.__version__}")
    except ImportError as e:
        errors.append(f"  ✗ pydantic: {e}")

    try:
        from pydantic import EmailStr
        print(f"  ✓ pydantic EmailStr (email-validator)")
    except ImportError as e:
        errors.append(f"  ✗ email-validator: {e}")

    try:
        import sqlalchemy
        print(f"  ✓ sqlalchemy {sqlalchemy.__version__}")
    except ImportError as e:
        errors.append(f"  ✗ sqlalchemy: {e}")

    try:
        import asyncpg
        print(f"  ✓ asyncpg {asyncpg.__version__}")
    except ImportError as e:
        errors.append(f"  ✗ asyncpg: {e}")

    try:
        import bcrypt
        print(f"  ✓ bcrypt {bcrypt.__version__}")
    except ImportError as e:
        errors.append(f"  ✗ bcrypt: {e}")

    try:
        import jose
        print(f"  ✓ python-jose")
    except ImportError as e:
        errors.append(f"  ✗ python-jose: {e}")

    try:
        import alembic
        print(f"  ✓ alembic {alembic.__version__}")
    except ImportError as e:
        errors.append(f"  ✗ alembic: {e}")

    # Check app imports
    print("\nChecking app modules...")

    try:
        from src.config import get_settings
        print("  ✓ src.config")
    except ImportError as e:
        errors.append(f"  ✗ src.config: {e}")

    try:
        from src.models import Base, User, Task
        print("  ✓ src.models")
    except ImportError as e:
        errors.append(f"  ✗ src.models: {e}")

    try:
        from src.schemas import UserRegisterRequest, TaskResponse, MessageResponse
        print("  ✓ src.schemas")
    except ImportError as e:
        errors.append(f"  ✗ src.schemas: {e}")

    try:
        from src.services import AuthService, TaskService
        print("  ✓ src.services")
    except ImportError as e:
        errors.append(f"  ✗ src.services: {e}")

    try:
        from src.middleware import get_current_user, RateLimitMiddleware
        print("  ✓ src.middleware")
    except ImportError as e:
        errors.append(f"  ✗ src.middleware: {e}")

    try:
        from src.db import get_db
        print("  ✓ src.db")
    except ImportError as e:
        errors.append(f"  ✗ src.db: {e}")

    try:
        from src.routes import api_router
        print("  ✓ src.routes")
    except ImportError as e:
        errors.append(f"  ✗ src.routes: {e}")

    try:
        from src.main import app
        print("  ✓ src.main (FastAPI app)")
    except ImportError as e:
        errors.append(f"  ✗ src.main: {e}")

    # Summary
    print("\n" + "="*50)
    if errors:
        print("ERRORS FOUND:")
        for err in errors:
            print(err)
        return False
    else:
        print("ALL IMPORTS SUCCESSFUL!")
        print("\nYou can now run:")
        print("  uvicorn src.main:app --reload --host 127.0.0.1 --port 8000")
        return True


if __name__ == "__main__":
    import sys
    success = check_imports()
    sys.exit(0 if success else 1)
