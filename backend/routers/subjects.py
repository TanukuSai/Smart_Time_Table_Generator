from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user, require_admin, get_admin_id

router = APIRouter()

class SubjectCreate(BaseModel):
    name: str
    code: str
    semester: int = 1
    classes_per_week: int = 4
    department_ids: list[int] = []
    type: str = 'theory'

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    semester: Optional[int] = None
    classes_per_week: Optional[int] = None
    department_ids: Optional[list[int]] = None
    type: Optional[str] = None

@router.get("")
async def list_subjects(db=Depends(get_db), user=Depends(get_current_user)):
    admin_id = get_admin_id(user)
    rows = await db.fetch("""
        SELECT s.*,
               COUNT(DISTINCT fs.faculty_id) as faculty_count
        FROM subjects s
        LEFT JOIN faculty_subjects fs ON s.id = fs.subject_id
        WHERE s.admin_id = $1
        GROUP BY s.id
        ORDER BY s.name
    """, admin_id)

    result = []
    for row in rows:
        faculty = [dict(f) for f in await db.fetch("""
            SELECT f.id, u.name, f.employee_code
            FROM faculty_subjects fs
            JOIN faculty f ON fs.faculty_id = f.id
            JOIN users u ON f.user_id = u.id
            WHERE fs.subject_id = $1
        """, row["id"])]

        departments = [dict(g) for g in await db.fetch("""
            SELECT DISTINCT g.id, g.name
            FROM departments g
            LEFT JOIN faculty_departments fg ON g.id = fg.department_id AND fg.subject_id = $1
            LEFT JOIN subject_departments sg ON g.id = sg.department_id AND sg.subject_id = $1
            WHERE (fg.subject_id IS NOT NULL OR sg.subject_id IS NOT NULL) AND g.admin_id = $2
            ORDER BY g.name
        """, row["id"], admin_id)]

        result.append({
            **dict(row),
            "faculty": faculty,
            "departments": departments
        })
    return result

@router.post("")
async def create_subject(body: SubjectCreate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    
    if body.type == 'lab' and body.classes_per_week > 3:
        raise HTTPException(400, "Lab subjects cannot exceed 3 hours per week")
        
    try:
        sid = await db.fetchval(
            "INSERT INTO subjects (name, code, semester, classes_per_week, admin_id, type) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
            body.name, body.code, body.semester, body.classes_per_week, admin_id, body.type
        )
        for gid in body.department_ids:
            await db.execute("INSERT INTO subject_departments (subject_id, department_id) VALUES ($1, $2) ON CONFLICT DO NOTHING", sid, gid)
        return {"id": sid, "message": "Subject created"}
    except Exception:
        raise HTTPException(400, "Subject name or code already exists")

@router.patch("/{subject_id}")
async def update_subject(subject_id: int, body: SubjectUpdate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id, type, classes_per_week FROM subjects WHERE id = $1 AND admin_id = $2", subject_id, admin_id)
    if not existing:
        raise HTTPException(404, "Subject not found")
        
    new_type = body.type if body.type is not None else existing['type']
    new_classes = body.classes_per_week if body.classes_per_week is not None else existing['classes_per_week']
    
    if new_type == 'lab' and new_classes > 3:
        raise HTTPException(400, "Lab subjects cannot exceed 3 hours per week")
        
    if body.name is not None:
        await db.execute("UPDATE subjects SET name = $1 WHERE id = $2", body.name, subject_id)
    if body.code is not None:
        await db.execute("UPDATE subjects SET code = $1 WHERE id = $2", body.code, subject_id)
    if body.semester is not None:
        await db.execute("UPDATE subjects SET semester = $1 WHERE id = $2", body.semester, subject_id)
    if body.classes_per_week is not None:
        await db.execute("UPDATE subjects SET classes_per_week = $1 WHERE id = $2", body.classes_per_week, subject_id)
    if body.type is not None:
        if body.type not in ('theory', 'lab'):
            raise HTTPException(400, "Invalid subject type")
        await db.execute("UPDATE subjects SET type = $1 WHERE id = $2", body.type, subject_id)
    if body.department_ids is not None:
        await db.execute("DELETE FROM subject_departments WHERE subject_id = $1", subject_id)
        for gid in body.department_ids:
            await db.execute("INSERT INTO subject_departments (subject_id, department_id) VALUES ($1, $2) ON CONFLICT DO NOTHING", subject_id, gid)
    return {"message": "Updated"}

@router.delete("/{subject_id}")
async def delete_subject(subject_id: int, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM subjects WHERE id = $1 AND admin_id = $2", subject_id, admin_id)
    if not existing:
        raise HTTPException(404, "Subject not found")
    await db.execute("DELETE FROM subjects WHERE id = $1", subject_id)
    return {"message": "Deleted"}
