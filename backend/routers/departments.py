from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user, require_admin, get_admin_id
from auth_utils import hash_password

router = APIRouter()

class DepartmentCreate(BaseModel):
    name: str
    level: str
    semester: int = 1
    section: str
    strength: int = 40
    room_id: Optional[int] = None
    lab_id: Optional[int] = None

class DepartmentUpdate(BaseModel):
    room_id: Optional[int] = None
    lab_id: Optional[int] = None

@router.get("")
async def list_departments(db=Depends(get_db), user=Depends(get_current_user)):
    admin_id = get_admin_id(user)
    rows = await db.fetch("""
        SELECT d.*, r.room_id as room_name, r2.room_id as lab_name
        FROM departments d 
        LEFT JOIN rooms r ON d.room_id = r.id 
        LEFT JOIN rooms r2 ON d.lab_id = r2.id
        WHERE d.admin_id = $1 
        ORDER BY d.name
    """, admin_id)
    # Attach student account info for each department
    result = []
    for r in rows:
        d = dict(r)
        stu = await db.fetchrow(
            "SELECT id, email, name FROM users WHERE role = 'student' AND department_id = $1 AND admin_id = $2",
            r["id"], admin_id
        )
        d["student_account"] = dict(stu) if stu else None
        result.append(d)
    return result

@router.post("")
async def create_department(body: DepartmentCreate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    try:
        if body.room_id:
            existing_dept = await db.fetchrow("SELECT name FROM departments WHERE room_id = $1 AND admin_id = $2", body.room_id, admin_id)
            if existing_dept:
                raise HTTPException(400, f"Classroom already assigned to department {existing_dept['name']}")
                
        async with db.transaction():
            gid = await db.fetchval(
                "INSERT INTO departments (name, level, semester, section, strength, admin_id, room_id, lab_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id",
                body.name, body.level, body.semester, body.section, body.strength, admin_id, body.room_id, body.lab_id
            )
            # Auto-create student account for this department
            stu_email = body.name.lower().replace(" ", "-") + f".{admin_id}@sttg.edu"
            stu_name = f"Student {body.name}"
            await db.execute(
                "INSERT INTO users (name, email, password_hash, role, admin_id, department_id) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING",
                stu_name, stu_email, hash_password("student123"), "student", admin_id, gid
            )
        return {"id": gid, "message": "Department added"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(400, "Department already exists or invalid data")

@router.patch("/{department_id}")
async def update_department(department_id: int, body: DepartmentUpdate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM departments WHERE id = $1 AND admin_id = $2", department_id, admin_id)
    if not existing:
        raise HTTPException(404, "Department not found")
        
    if body.room_id is not None:
        collision = await db.fetchrow("SELECT name FROM departments WHERE room_id = $1 AND admin_id = $2 AND id != $3", body.room_id, admin_id, department_id)
        if collision:
            raise HTTPException(400, f"Classroom already assigned to department {collision['name']}")
        await db.execute("UPDATE departments SET room_id = $1 WHERE id = $2", body.room_id, department_id)
        
    if body.lab_id is not None:
        await db.execute("UPDATE departments SET lab_id = $1 WHERE id = $2", body.lab_id, department_id)
        
    return {"message": "Department updated"}

@router.delete("/{department_id}")
async def delete_department(department_id: int, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM departments WHERE id = $1 AND admin_id = $2", department_id, admin_id)
    if not existing:
        raise HTTPException(404, "Department not found")
    # Delete associated student account
    await db.execute("DELETE FROM users WHERE role = 'student' AND department_id = $1 AND admin_id = $2", department_id, admin_id)
    await db.execute("DELETE FROM departments WHERE id = $1", department_id)
    return {"message": "Deleted"}
