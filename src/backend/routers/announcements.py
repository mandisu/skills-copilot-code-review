"""
Endpoints for announcement management in the High School Management System API
"""

from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from ..database import announcements_collection
from .auth import get_authenticated_teacher

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


class AnnouncementPayload(BaseModel):
    message: str
    start_date: Optional[str] = None
    expiration_date: str


def _parse_date(value: Optional[str], field_name: str) -> Optional[date]:
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} must use YYYY-MM-DD format"
        ) from exc


def _require_teacher(authorization: Optional[str]) -> None:
    get_authenticated_teacher(authorization)


def _validate_payload(payload: AnnouncementPayload) -> Dict[str, Any]:
    message = payload.message.strip()
    if not message:
        raise HTTPException(
            status_code=400, detail="Announcement message is required")

    start_date = _parse_date(payload.start_date, "Start date")
    expiration_date = _parse_date(payload.expiration_date, "Expiration date")

    if not expiration_date:
        raise HTTPException(
            status_code=400, detail="Expiration date is required")

    if start_date and start_date > expiration_date:
        raise HTTPException(
            status_code=400,
            detail="Start date must be on or before the expiration date"
        )

    return {
        "message": message,
        "start_date": start_date,
        "expiration_date": expiration_date,
    }


def _serialize_announcement(announcement: Dict[str, Any]) -> Dict[str, Any]:
    today = date.today()
    start_date = _parse_date(announcement.get("start_date"), "Start date")
    expiration_date = _parse_date(
        announcement.get("expiration_date"), "Expiration date")

    is_active = bool(
        expiration_date and expiration_date >= today and
        (start_date is None or start_date <= today)
    )

    return {
        "id": str(announcement["_id"]),
        "message": announcement["message"],
        "start_date": announcement.get("start_date"),
        "expiration_date": announcement.get("expiration_date"),
        "created_at": announcement.get("created_at"),
        "updated_at": announcement.get("updated_at"),
        "is_active": is_active,
    }


@router.get("")
@router.get("/")
def get_announcements() -> List[Dict[str, Any]]:
    announcements = []
    for announcement in announcements_collection.find().sort([
        ("created_at", -1)
    ]):
        announcements.append(_serialize_announcement(announcement))

    return announcements


@router.get("/active")
def get_active_announcements() -> List[Dict[str, Any]]:
    return [
        announcement for announcement in get_announcements()
        if announcement["is_active"]
    ]


@router.post("", status_code=201)
@router.post("/", status_code=201)
def create_announcement(
    payload: AnnouncementPayload,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    _require_teacher(authorization)
    values = _validate_payload(payload)

    now = datetime.utcnow().isoformat()
    announcement = {
        "_id": f"announcement-{uuid4().hex}",
        "message": values["message"],
        "start_date": values["start_date"].isoformat() if values["start_date"] else None,
        "expiration_date": values["expiration_date"].isoformat(),
        "created_at": now,
        "updated_at": now,
    }

    announcements_collection.insert_one(announcement)
    return _serialize_announcement(announcement)


@router.put("/{announcement_id}")
def update_announcement(
    announcement_id: str,
    payload: AnnouncementPayload,
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    _require_teacher(authorization)
    values = _validate_payload(payload)

    announcement = announcements_collection.find_one({"_id": announcement_id})
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")

    updated_fields = {
        "message": values["message"],
        "start_date": values["start_date"].isoformat() if values["start_date"] else None,
        "expiration_date": values["expiration_date"].isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    result = announcements_collection.update_one(
        {"_id": announcement_id},
        {"$set": updated_fields}
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=500, detail="Failed to update announcement")

    announcement.update(updated_fields)
    return _serialize_announcement(announcement)


@router.delete("/{announcement_id}")
def delete_announcement(
    announcement_id: str,
    authorization: Optional[str] = Header(None)
) -> Dict[str, str]:
    _require_teacher(authorization)

    result = announcements_collection.delete_one({"_id": announcement_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Announcement not found")

    return {"message": "Announcement deleted"}
