"""
Authentication endpoints for the High School Management System API
"""

import secrets
from typing import Any, Dict, Optional

from fastapi import APIRouter, Header, HTTPException

from ..database import teachers_collection, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

active_sessions: Dict[str, str] = {}


def _extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    return token.strip()


def get_authenticated_teacher(authorization: Optional[str]) -> Dict[str, Any]:
    token = _extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")

    username = active_sessions.get(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        active_sessions.pop(token, None)
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    return teacher


@router.post("/login")
def login(username: str, password: str) -> Dict[str, Any]:
    """Login a teacher account"""
    # Find the teacher in the database
    teacher = teachers_collection.find_one({"_id": username})

    # Verify password using Argon2 verifier from database.py
    if not teacher or not verify_password(teacher.get("password", ""), password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password")

    token = secrets.token_urlsafe(32)
    active_sessions[token] = teacher["username"]

    # Return teacher information (excluding password)
    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"],
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/check-session")
def check_session(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Check if a session token is valid"""
    teacher = get_authenticated_teacher(authorization)

    return {
        "username": teacher["username"],
        "display_name": teacher["display_name"],
        "role": teacher["role"]
    }
