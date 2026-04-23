from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user, require_admin, get_admin_id
import json

router = APIRouter()

# Categories that cannot be disabled
MANDATORY_CATEGORIES = {"no_faculty_double_booking", "no_room_double_booking"}

class ConstraintCreate(BaseModel):
    name: str
    type: str = "hard"
    category: str
    config: dict = {}

class ConstraintUpdate(BaseModel):
    is_enabled: Optional[int] = None
    name: Optional[str] = None

@router.get("")
async def list_constraints(db=Depends(get_db), user=Depends(get_current_user)):
    admin_id = get_admin_id(user)
    rows = await db.fetch(
        "SELECT * FROM constraints WHERE admin_id = $1 ORDER BY is_builtin DESC, created_at ASC",
        admin_id
    )
    result = []
    for row in rows:
        d = dict(row)
        # Ensure config is a dict (asyncpg returns JSONB as dict)
        if isinstance(d.get("config"), str):
            d["config"] = json.loads(d["config"])
        result.append(d)
    return result

@router.post("")
async def create_constraint(body: ConstraintCreate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    if body.type not in ("hard", "soft"):
        raise HTTPException(400, "Type must be 'hard' or 'soft'")

    cid = await db.fetchval("""
        INSERT INTO constraints (name, type, category, is_enabled, is_builtin, config, admin_id)
        VALUES ($1, $2, $3, 1, 0, $4::jsonb, $5) RETURNING id
    """, body.name, body.type, body.category, json.dumps(body.config), admin_id)
    return {"id": cid, "message": "Constraint created"}

@router.patch("/{constraint_id}")
async def update_constraint(constraint_id: int, body: ConstraintUpdate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    row = await db.fetchrow("SELECT * FROM constraints WHERE id = $1 AND admin_id = $2", constraint_id, admin_id)
    if not row:
        raise HTTPException(404, "Constraint not found")

    if body.is_enabled is not None:
        # Prevent disabling mandatory constraints
        if row["is_builtin"] == 1 and row["category"] in MANDATORY_CATEGORIES and body.is_enabled == 0:
            raise HTTPException(400, "This constraint cannot be disabled — it's required for correct scheduling")
        await db.execute("UPDATE constraints SET is_enabled = $1 WHERE id = $2", body.is_enabled, constraint_id)

    if body.name is not None:
        if row["is_builtin"] == 1:
            raise HTTPException(400, "Cannot rename built-in constraints")
        await db.execute("UPDATE constraints SET name = $1 WHERE id = $2", body.name, constraint_id)

    return {"message": "Updated"}

@router.delete("/{constraint_id}")
async def delete_constraint(constraint_id: int, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    row = await db.fetchrow("SELECT is_builtin FROM constraints WHERE id = $1 AND admin_id = $2", constraint_id, admin_id)
    if not row:
        raise HTTPException(404, "Constraint not found")
    if row["is_builtin"] == 1:
        raise HTTPException(400, "Cannot delete built-in constraints")
    await db.execute("DELETE FROM constraints WHERE id = $1", constraint_id)
    return {"message": "Deleted"}
