from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from routers.auth import get_current_user, require_admin, get_admin_id
from auth_utils import hash_password

router = APIRouter()

class FacultyCreate(BaseModel):
    name: str
    email: str
    password: str = "faculty123"
    employee_code: str
    max_weekly_hours: int = 20
    subject_ids: List[int] = []
    grade_subject_pairs: List[dict] = []  # [{department_id, subject_id}]

class FacultyUpdate(BaseModel):
    max_weekly_hours: Optional[int] = None
    is_present: Optional[int] = None
    subject_ids: Optional[List[int]] = None
    grade_subject_pairs: Optional[List[dict]] = None

@router.get("")
async def list_faculty(db=Depends(get_db), user=Depends(get_current_user), date: Optional[str] = None):
    admin_id = get_admin_id(user)
    from datetime import date as dt_date, datetime
    if date:
        try:
            today_str = datetime.strptime(date, "%Y-%m-%d").date().isoformat()
        except ValueError:
            today_str = dt_date.today().isoformat()
    else:
        today_str = dt_date.today().isoformat()

    rows = await db.fetch("""
        SELECT f.id, f.employee_code, f.max_weekly_hours, f.is_present as manual_is_present,
               u.name, u.email, u.id as user_id,
               EXISTS(
                   SELECT 1 FROM leave_requests lr
                   WHERE lr.faculty_id = f.id AND lr.status = 'approved' AND lr.leave_date = $2
               ) as on_leave_today
        FROM faculty f JOIN users u ON f.user_id = u.id
        WHERE f.admin_id = $1
        ORDER BY u.name
    """, admin_id, today_str)

    result = []
    for row in rows:
        fid = row["id"]
        subjects = [dict(r) for r in await db.fetch("""
            SELECT s.id, s.name, s.code FROM faculty_subjects fs
            JOIN subjects s ON fs.subject_id = s.id WHERE fs.faculty_id = $1
        """, fid)]

        grade_subjects = [dict(r) for r in await db.fetch("""
            SELECT g.id as department_id, g.name as grade_name,
                   s.id as subject_id, s.name as subject_name
            FROM faculty_departments fg
            JOIN departments g ON fg.department_id = g.id
            JOIN subjects s ON fg.subject_id = s.id
            WHERE fg.faculty_id = $1
            ORDER BY g.name
        """, fid)]

        row_dict = dict(row)
        is_present = 0 if row_dict["on_leave_today"] else row_dict["manual_is_present"]
        del row_dict["on_leave_today"]
        del row_dict["manual_is_present"]
        row_dict["is_present"] = is_present

        result.append({**row_dict, "subjects": subjects, "grade_subjects": grade_subjects})
    return result

@router.post("")
async def create_faculty(body: FacultyCreate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM users WHERE email = $1", body.email)
    if existing:
        raise HTTPException(400, "Email already exists")

    async with db.transaction():
        user_id = await db.fetchval(
            "INSERT INTO users (name, email, password_hash, role, admin_id) VALUES ($1, $2, $3, $4, $5) RETURNING id",
            body.name, body.email, hash_password(body.password), "faculty", admin_id
        )

        fac_id = await db.fetchval(
            "INSERT INTO faculty (user_id, employee_code, max_weekly_hours, admin_id) VALUES ($1, $2, $3, $4) RETURNING id",
            user_id, body.employee_code, body.max_weekly_hours, admin_id
        )

        for sid in body.subject_ids:
            await db.execute(
                "INSERT INTO faculty_subjects (faculty_id, subject_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                fac_id, sid
            )

        for pair in body.grade_subject_pairs:
            await db.execute(
                "INSERT INTO faculty_departments (faculty_id, department_id, subject_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                fac_id, pair["department_id"], pair["subject_id"]
            )

    return {"id": fac_id, "message": "Faculty created"}

@router.patch("/{fac_id}")
async def update_faculty(fac_id: int, body: FacultyUpdate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM faculty WHERE id = $1 AND admin_id = $2", fac_id, admin_id)
    if not existing:
        raise HTTPException(404, "Faculty not found")
    async with db.transaction():
        if body.is_present is not None:
            await db.execute("UPDATE faculty SET is_present = $1 WHERE id = $2", body.is_present, fac_id)
        if body.max_weekly_hours is not None:
            await db.execute("UPDATE faculty SET max_weekly_hours = $1 WHERE id = $2", body.max_weekly_hours, fac_id)
        if body.subject_ids is not None:
            await db.execute("DELETE FROM faculty_subjects WHERE faculty_id = $1", fac_id)
            for sid in body.subject_ids:
                await db.execute(
                    "INSERT INTO faculty_subjects (faculty_id, subject_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                    fac_id, sid
                )
        if body.grade_subject_pairs is not None:
            await db.execute("DELETE FROM faculty_departments WHERE faculty_id = $1", fac_id)
            for pair in body.grade_subject_pairs:
                await db.execute(
                    "INSERT INTO faculty_departments (faculty_id, department_id, subject_id) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                    fac_id, pair["department_id"], pair["subject_id"]
                )
    return {"message": "Updated"}

@router.delete("/{fac_id}")
async def delete_faculty(fac_id: int, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    row = await db.fetchrow("SELECT user_id FROM faculty WHERE id = $1 AND admin_id = $2", fac_id, admin_id)
    if not row:
        raise HTTPException(404, "Faculty not found")
    await db.execute("DELETE FROM users WHERE id = $1", row["user_id"])
    return {"message": "Deleted"}

@router.get("/me/schedule")
async def my_schedule(db=Depends(get_db), user=Depends(get_current_user), date: Optional[str] = None):
    if user["role"] != "faculty":
        raise HTTPException(403, "Faculty only")
    fac = await db.fetchrow("SELECT id FROM faculty WHERE user_id = $1", int(user["sub"]))
    if not fac:
        raise HTTPException(404, "Faculty profile not found")

    rows = await db.fetch("""
        SELECT ts.day, ts.slot_index, ts.slot_time, ts.is_break,
               s.name as subject_name, g.name as grade_name, r.room_id
        FROM timetable_slots ts
        LEFT JOIN subjects s ON ts.subject_id = s.id
        LEFT JOIN departments g ON ts.department_id = g.id
        LEFT JOIN rooms r ON ts.room_id = r.id
        WHERE ts.faculty_id = $1
        ORDER BY ts.day, ts.slot_index
    """, fac["id"])

    result = [dict(r) for r in rows]

    # Overlay substitution duties
    from datetime import date as dt_date, timedelta, datetime
    if date:
        try:
            today = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            today = dt_date.today()
    else:
        today = dt_date.today()
        
    tomorrow = today + timedelta(days=1)
    today_str = today.isoformat()
    tomorrow_str = tomorrow.isoformat()

    sub_rows = await db.fetch("""
        SELECT sub.day, sub.slot_index, sub.department_id, sub.subject_id,
               u_orig.name as original_faculty_name,
               s.name as subject_name,
               g.name as grade_name,
               ts.slot_time,
               lr.leave_date,
               sub.original_faculty_id,
               sub.substitute_faculty_id
        FROM substitutions sub
        JOIN leave_requests lr ON sub.leave_request_id = lr.id
        LEFT JOIN faculty f_orig ON sub.original_faculty_id = f_orig.id
        LEFT JOIN users u_orig ON f_orig.user_id = u_orig.id
        LEFT JOIN faculty f_sub ON sub.substitute_faculty_id = f_sub.id
        LEFT JOIN users u_sub ON f_sub.user_id = u_sub.id
        LEFT JOIN subjects s ON sub.subject_id = s.id
        LEFT JOIN departments g ON sub.department_id = g.id
        LEFT JOIN timetable_slots ts ON sub.timetable_slot_id = ts.id
        WHERE (sub.substitute_faculty_id = $1 OR sub.original_faculty_id = $1)
          AND lr.status = 'approved'
          AND sub.status IN ('auto_assigned', 'no_substitute', 'manually_assigned')
          AND lr.leave_date IN ($2, $3)
    """, fac["id"], today_str, tomorrow_str)

    for sr in sub_rows:
        is_sub = sr["substitute_faculty_id"] == fac["id"]
        result.append({
            "day": sr["day"],
            "slot_index": sr["slot_index"],
            "slot_time": sr["slot_time"],
            "is_break": False,
            "subject_name": sr["subject_name"],
            "grade_name": sr["grade_name"],
            "room_id": None,
            "is_substitution": is_sub,
            "is_absent": not is_sub,
            "substitute_faculty_name": sr["substitute_faculty_name"],
            "original_faculty_name": sr["original_faculty_name"],
            "leave_date": sr["leave_date"]
        })

    return result


@router.get("/me/substitutions")
async def my_substitutions(db=Depends(get_db), user=Depends(get_current_user), date: Optional[str] = None):
    """Get all upcoming substitution assignments for the logged-in faculty."""
    if user["role"] != "faculty":
        raise HTTPException(403, "Faculty only")
    fac = await db.fetchrow("SELECT id FROM faculty WHERE user_id = $1", int(user["sub"]))
    if not fac:
        raise HTTPException(404, "Faculty profile not found")

    from datetime import date as dt_date, datetime
    if date:
        try:
            today_str = datetime.strptime(date, "%Y-%m-%d").date().isoformat()
        except ValueError:
            today_str = dt_date.today().isoformat()
    else:
        today_str = dt_date.today().isoformat()

    rows = await db.fetch("""
        SELECT sub.day, sub.slot_index, sub.department_id, sub.subject_id,
               sub.status,
               u_orig.name as original_faculty_name,
               s.name as subject_name,
               g.name as department_name,
               ts.slot_time,
               lr.leave_date
        FROM substitutions sub
        JOIN leave_requests lr ON sub.leave_request_id = lr.id
        LEFT JOIN faculty f_orig ON sub.original_faculty_id = f_orig.id
        LEFT JOIN users u_orig ON f_orig.user_id = u_orig.id
        LEFT JOIN subjects s ON sub.subject_id = s.id
        LEFT JOIN departments g ON sub.department_id = g.id
        LEFT JOIN timetable_slots ts ON sub.timetable_slot_id = ts.id
        WHERE sub.substitute_faculty_id = $1
          AND lr.status = 'approved'
          AND sub.status IN ('auto_assigned', 'manually_assigned')
          AND lr.leave_date >= $2
        ORDER BY lr.leave_date ASC, sub.slot_index ASC
    """, fac["id"], today_str)

    return [dict(r) for r in rows]
