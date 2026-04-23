from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user, require_admin, get_admin_id

router = APIRouter()

class RoomCreate(BaseModel):
    room_id: str
    type: str
    capacity: int

class RoomUpdate(BaseModel):
    is_available: Optional[int] = None
    capacity: Optional[int] = None

@router.get("")
async def list_rooms(db=Depends(get_db), user=Depends(get_current_user)):
    admin_id = get_admin_id(user)
    rows = await db.fetch("SELECT * FROM rooms WHERE admin_id = $1 ORDER BY room_id", admin_id)
    return [dict(r) for r in rows]

@router.post("")
async def create_room(body: RoomCreate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    try:
        rid = await db.fetchval(
            "INSERT INTO rooms (room_id, type, capacity, admin_id) VALUES ($1, $2, $3, $4) RETURNING id",
            body.room_id, body.type, body.capacity, admin_id
        )
        return {"id": rid, "message": "Room added"}
    except Exception:
        raise HTTPException(400, "Room ID already exists")

@router.patch("/{room_id}")
async def update_room(room_id: int, body: RoomUpdate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM rooms WHERE id = $1 AND admin_id = $2", room_id, admin_id)
    if not existing:
        raise HTTPException(404, "Room not found")
    if body.is_available is not None:
        await db.execute("UPDATE rooms SET is_available = $1 WHERE id = $2", body.is_available, room_id)
    if body.capacity is not None:
        await db.execute("UPDATE rooms SET capacity = $1 WHERE id = $2", body.capacity, room_id)
    return {"message": "Updated"}

@router.delete("/{room_id}")
async def delete_room(room_id: int, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM rooms WHERE id = $1 AND admin_id = $2", room_id, admin_id)
    if not existing:
        raise HTTPException(404, "Room not found")
    await db.execute("DELETE FROM rooms WHERE id = $1", room_id)
    return {"message": "Deleted"}
