from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_db
from routers.auth import get_current_user, require_admin, get_admin_id
from datetime import datetime
import json

router = APIRouter()

# Map date strings to day names for timetable lookup
WEEKDAY_MAP = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}

class LeaveCreate(BaseModel):
    leave_date: str
    reason: str
    leave_type: str = "casual"

class LeaveReview(BaseModel):
    status: str  # approved | denied
    admin_note: Optional[str] = None

class EmergencyLeaveCreate(BaseModel):
    faculty_id: int
    reason: str = "Emergency Sick Leave (Admin)"

@router.get("")
async def list_leaves(status: Optional[str] = None, db=Depends(get_db), user=Depends(get_current_user)):
    admin_id = get_admin_id(user)

    if user["role"] == "faculty":
        rows = await db.fetch("""
            SELECT lr.*, u.name as faculty_name, f.employee_code, f.id as faculty_id
            FROM leave_requests lr
            JOIN faculty f ON lr.faculty_id = f.id
            JOIN users u ON f.user_id = u.id
            WHERE f.user_id = $1
            ORDER BY lr.created_at DESC
        """, int(user["sub"]))
    elif status:
        rows = await db.fetch("""
            SELECT lr.*, u.name as faculty_name, f.employee_code, f.id as faculty_id
            FROM leave_requests lr
            JOIN faculty f ON lr.faculty_id = f.id
            JOIN users u ON f.user_id = u.id
            WHERE lr.status = $1 AND f.admin_id = $2
            ORDER BY lr.created_at DESC
        """, status, admin_id)
    else:
        rows = await db.fetch("""
            SELECT lr.*, u.name as faculty_name, f.employee_code, f.id as faculty_id
            FROM leave_requests lr
            JOIN faculty f ON lr.faculty_id = f.id
            JOIN users u ON f.user_id = u.id
            WHERE f.admin_id = $1
            ORDER BY lr.created_at DESC
        """, admin_id)

    result = []
    for row in rows:
        fid = row["faculty_id"]
        departments = [r["name"] for r in await db.fetch("""
            SELECT DISTINCT g.name FROM faculty_departments fg
            JOIN departments g ON fg.department_id = g.id
            WHERE fg.faculty_id = $1
        """, fid)]

        # Attach substitutions for this leave
        subs = await db.fetch("""
            SELECT sub.*, 
                   u_orig.name as original_faculty_name,
                   u_sub.name as substitute_faculty_name,
                   s.name as subject_name,
                   d.name as department_name,
                   ts.slot_time
            FROM substitutions sub
            LEFT JOIN faculty f_orig ON sub.original_faculty_id = f_orig.id
            LEFT JOIN users u_orig ON f_orig.user_id = u_orig.id
            LEFT JOIN faculty f_sub ON sub.substitute_faculty_id = f_sub.id
            LEFT JOIN users u_sub ON f_sub.user_id = u_sub.id
            LEFT JOIN subjects s ON sub.subject_id = s.id
            LEFT JOIN departments d ON sub.department_id = d.id
            LEFT JOIN timetable_slots ts ON sub.timetable_slot_id = ts.id
            WHERE sub.leave_request_id = $1
            ORDER BY sub.slot_index
        """, row["id"])

        result.append({
            **dict(row),
            "affected_departments": departments,
            "substitutions": [dict(s) for s in subs]
        })
    return result

@router.post("")
async def create_leave(body: LeaveCreate, db=Depends(get_db), user=Depends(get_current_user)):
    if user["role"] != "faculty":
        raise HTTPException(403, "Faculty only")
    fac = await db.fetchrow("SELECT id FROM faculty WHERE user_id = $1", int(user["sub"]))
    if not fac:
        raise HTTPException(404, "Faculty profile not found")
    await db.execute("""
        INSERT INTO leave_requests (faculty_id, leave_date, reason, leave_type)
        VALUES ($1, $2, $3, $4)
    """, fac["id"], body.leave_date, body.reason, body.leave_type)
    return {"message": "Leave request submitted"}

@router.post("/emergency")
async def create_emergency_leave(body: EmergencyLeaveCreate, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)

    # Verify faculty belongs to this admin
    fac = await db.fetchrow("SELECT id, user_id FROM faculty WHERE id = $1 AND admin_id = $2", body.faculty_id, admin_id)
    if not fac:
        raise HTTPException(404, "Faculty not found")

    from datetime import date
    today_str = date.today().isoformat()

    # Check if a leave request already exists for today
    existing = await db.fetchrow(
        "SELECT id FROM leave_requests WHERE faculty_id = $1 AND leave_date = $2",
        body.faculty_id, today_str
    )
    if existing:
        raise HTTPException(400, "A leave request already exists for this faculty today")

    async with db.transaction():
        # Insert approved leave request
        leave_id = await db.fetchval("""
            INSERT INTO leave_requests (faculty_id, leave_date, reason, leave_type, status, reviewed_at, admin_note)
            VALUES ($1, $2, $3, 'sick', 'approved', $4, 'Triggered by admin')
            RETURNING id
        """, body.faculty_id, today_str, body.reason, datetime.utcnow())

        leave = await db.fetchrow("SELECT * FROM leave_requests WHERE id = $1", leave_id)

        # Run smart substitution engine
        substitutions = await _find_substitutions(db, leave, admin_id, leave_id)

        history_id = None
        if substitutions:
            import json
            # Build a mini snapshot showing only the affected slots
            fac_name_row = await db.fetchrow("SELECT u.name FROM users u WHERE u.id = $1", fac["user_id"])
            fac_name = fac_name_row["name"] if fac_name_row else "Unknown"

            # Get affected department IDs
            dept_ids = list(set(s.get("department_id") or 0 for s in substitutions if isinstance(s, dict)))
            dept_ids = [d for d in dept_ids if d]
            if not dept_ids:
                sub_rows = await db.fetch(
                    "SELECT DISTINCT department_id FROM substitutions WHERE leave_request_id = $1", leave_id
                )
                dept_ids = [r["department_id"] for r in sub_rows if r["department_id"]]

            snapshot = {}
            for sub in substitutions:
                dept_name = sub.get("department_name", "Unknown")
                day = sub.get("day", "Mon")
                if dept_name not in snapshot:
                    snapshot[dept_name] = {}
                if day not in snapshot[dept_name]:
                    snapshot[dept_name][day] = []
                snapshot[dept_name][day].append({
                    "slot_index": sub.get("slot_index", 0),
                    "slot_time": sub.get("slot_time", ""),
                    "subject": sub.get("subject_name"),
                    "faculty": sub.get("substitute_faculty_name"),
                    "original_faculty": fac_name,
                    "is_break": 0,
                    "is_substitution": True
                })

            history_name = f"Emergency Substitution — {fac_name} on {today_str}"
            history_id = await db.fetchval("""
                INSERT INTO timetable_history (admin_id, name, department_ids, snapshot, log, status, type, leave_request_id)
                VALUES ($1, $2, $3::jsonb, $4::jsonb, $5, 'draft', 'substitution', $6)
                RETURNING id
            """,
                admin_id, history_name, json.dumps(dept_ids), json.dumps(snapshot),
                f"Auto-generated emergency substitution for {fac_name} on {today_str}",
                leave_id
            )

    return {"message": "Emergency leave created and substitutions assigned", "substitutions": substitutions}

@router.patch("/{leave_id}/review")
async def review_leave(leave_id: int, body: LeaveReview, db=Depends(get_db), user=Depends(require_admin)):
    if body.status not in ("approved", "denied"):
        raise HTTPException(400, "Status must be 'approved' or 'denied'")

    admin_id = get_admin_id(user)

    # Get leave details
    leave = await db.fetchrow("""
        SELECT lr.*, f.id as faculty_id FROM leave_requests lr
        JOIN faculty f ON lr.faculty_id = f.id
        WHERE lr.id = $1
    """, leave_id)
    if not leave:
        raise HTTPException(404, "Leave not found")

    async with db.transaction():
        # Update leave status
        await db.execute("""
            UPDATE leave_requests SET status = $1, admin_note = $2, reviewed_at = $3
            WHERE id = $4
        """, body.status, body.admin_note, datetime.utcnow(), leave_id)

        # If approved → run smart substitution engine
        if body.status == "approved":

            substitutions = await _find_substitutions(db, leave, admin_id, leave_id)

            # Create a draft substitution timetable entry in history
            history_id = None
            if substitutions:
                import json
                # Build a mini snapshot showing only the affected slots
                fac_name_row = await db.fetchrow("""
                    SELECT u.name FROM faculty f JOIN users u ON f.user_id = u.id WHERE f.id = $1
                """, leave["faculty_id"])
                fac_name = fac_name_row["name"] if fac_name_row else "Unknown"

                # Get affected department IDs
                dept_ids = list(set(s.get("department_id") or 0 for s in substitutions if isinstance(s, dict)))
                # Filter out 0s
                dept_ids = [d for d in dept_ids if d]
                if not dept_ids:
                    # Fallback: get from substitution records in DB
                    sub_rows = await db.fetch(
                        "SELECT DISTINCT department_id FROM substitutions WHERE leave_request_id = $1",
                        leave_id
                    )
                    dept_ids = [r["department_id"] for r in sub_rows if r["department_id"]]

                snapshot = {}
                for sub in substitutions:
                    dept_name = sub.get("department_name", "Unknown")
                    day = sub.get("day", "Mon")
                    if dept_name not in snapshot:
                        snapshot[dept_name] = {}
                    if day not in snapshot[dept_name]:
                        snapshot[dept_name][day] = []
                    snapshot[dept_name][day].append({
                        "slot_index": sub.get("slot_index", 0),
                        "slot_time": sub.get("slot_time", ""),
                        "subject": sub.get("subject_name"),
                        "faculty": sub.get("substitute_faculty_name"),
                        "original_faculty": fac_name,
                        "is_break": 0,
                        "is_substitution": True
                    })

                history_name = f"Substitution — {fac_name} on {leave['leave_date']}"
                history_id = await db.fetchval("""
                    INSERT INTO timetable_history (admin_id, name, department_ids, snapshot, log, status, type, leave_request_id)
                    VALUES ($1, $2, $3::jsonb, $4::jsonb, $5, 'draft', 'substitution', $6)
                    RETURNING id
                """,
                    admin_id, history_name, json.dumps(dept_ids), json.dumps(snapshot),
                    f"Auto-generated substitution for {fac_name} on {leave['leave_date']}",
                    leave_id
                )

            return {
                "message": "Leave approved",
                "substitutions": substitutions,
                "history_id": history_id
            }

        # If denied → no further action needed
        if body.status == "denied":
            pass

    return {"message": f"Leave {body.status}"}


async def _find_substitutions(db, leave, admin_id: int, leave_id: int) -> list:
    """
    Smart Substitution Engine:
    1. Parse the leave date to find the day of week (Mon, Tue, etc.)
    2. Find all timetable slots for the absent faculty on that day
    3. For each slot, find substitute candidates ranked by:
       - Can teach the same subject (faculty_subjects match)
       - Is present (is_present = 1)
       - Not already teaching at that time slot on that day
       - Lowest current weekly workload (fewest assigned slots)
    4. Auto-assign the best candidate and store in substitutions table
    """
    faculty_id = leave["faculty_id"]
    leave_date_str = leave["leave_date"]

    # Parse leave date to get day of week
    try:
        # Try multiple date formats
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y"):
            try:
                leave_dt = datetime.strptime(leave_date_str, fmt)
                break
            except ValueError:
                continue
        else:
            return []  # Can't parse date

        weekday = leave_dt.weekday()  # 0=Mon, 4=Fri
        if weekday > 4:
            return []  # Weekend, no classes

        day_name = WEEKDAY_MAP[weekday]
    except Exception:
        return []

    # Find all timetable slots where this faculty teaches on that day
    slots = await db.fetch("""
        SELECT ts.id, ts.department_id, ts.day, ts.slot_index, ts.slot_time, 
               ts.subject_id, ts.room_id, ts.is_break,
               s.name as subject_name, s.code as subject_code,
               d.name as department_name
        FROM timetable_slots ts
        LEFT JOIN subjects s ON ts.subject_id = s.id
        LEFT JOIN departments d ON ts.department_id = d.id
        WHERE ts.faculty_id = $1 AND ts.day = $2 AND ts.is_break = 0 AND ts.admin_id = $3
        ORDER BY ts.slot_index
    """, faculty_id, day_name, admin_id)

    if not slots:
        return []

    # Delete any previous substitutions for this leave
    await db.execute("DELETE FROM substitutions WHERE leave_request_id = $1", leave_id)

    substitution_results = []

    for slot in slots:
        subject_id = slot["subject_id"]
        slot_index = slot["slot_index"]

        if not subject_id:
            continue

        # Find substitute candidates:
        # 1. Must be able to teach this subject (faculty_subjects)
        # 2. Must be present (is_present = 1)
        # 3. Must NOT be the absent faculty
        # 4. Must NOT be already teaching at this time slot on this day
        # 5. Must belong to the same admin
        # 6. Ranked by fewest total assigned timetable slots (lowest workload)
        candidates = await db.fetch("""
            SELECT f.id as faculty_id, u.name as faculty_name, f.employee_code,
                   f.max_weekly_hours,
                   (SELECT COUNT(*) FROM timetable_slots ts2 WHERE ts2.faculty_id = f.id) as current_hours
            FROM faculty f
            JOIN users u ON f.user_id = u.id
            JOIN faculty_subjects fs ON f.id = fs.faculty_id AND fs.subject_id = $1
            WHERE f.admin_id = $2
              AND f.is_present = 1
              AND f.id != $3
              AND f.id NOT IN (
                  SELECT ts3.faculty_id FROM timetable_slots ts3
                  WHERE ts3.day = $4 AND ts3.slot_index = $5 AND ts3.faculty_id IS NOT NULL
              )
            ORDER BY current_hours ASC, f.max_weekly_hours DESC
            LIMIT 5
        """, subject_id, admin_id, faculty_id, day_name, slot_index)

        best = candidates[0] if candidates else None

        sub_record = {
            "day": day_name,
            "slot_index": slot_index,
            "slot_time": slot["slot_time"],
            "subject_name": slot["subject_name"],
            "department_name": slot["department_name"],
            "original_faculty_id": faculty_id,
            "substitute_faculty_id": best["faculty_id"] if best else None,
            "substitute_faculty_name": best["faculty_name"] if best else None,
            "substitute_employee_code": best["employee_code"] if best else None,
            "status": "auto_assigned" if best else "no_substitute",
            "candidates": [
                {"name": c["faculty_name"], "code": c["employee_code"], "hours": c["current_hours"]}
                for c in candidates
            ]
        }

        # Save to database
        await db.execute("""
            INSERT INTO substitutions 
            (leave_request_id, timetable_slot_id, original_faculty_id, substitute_faculty_id,
             department_id, day, slot_index, subject_id, status, admin_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
            leave_id, slot["id"], faculty_id,
            best["faculty_id"] if best else None,
            slot["department_id"], day_name, slot_index,
            subject_id,
            "auto_assigned" if best else "no_substitute",
            admin_id
        )

        substitution_results.append(sub_record)

    return substitution_results


@router.get("/substitutions")
async def list_substitutions(db=Depends(get_db), user=Depends(get_current_user)):
    """List all active substitutions for this admin"""
    admin_id = get_admin_id(user)
    rows = await db.fetch("""
        SELECT sub.*,
               u_orig.name as original_faculty_name, f_orig.employee_code as original_employee_code,
               u_sub.name as substitute_faculty_name, f_sub.employee_code as substitute_employee_code,
               s.name as subject_name,
               d.name as department_name,
               ts.slot_time,
               lr.leave_date
        FROM substitutions sub
        JOIN leave_requests lr ON sub.leave_request_id = lr.id
        LEFT JOIN faculty f_orig ON sub.original_faculty_id = f_orig.id
        LEFT JOIN users u_orig ON f_orig.user_id = u_orig.id
        LEFT JOIN faculty f_sub ON sub.substitute_faculty_id = f_sub.id
        LEFT JOIN users u_sub ON f_sub.user_id = u_sub.id
        LEFT JOIN subjects s ON sub.subject_id = s.id
        LEFT JOIN departments d ON sub.department_id = d.id
        LEFT JOIN timetable_slots ts ON sub.timetable_slot_id = ts.id
        WHERE sub.admin_id = $1
        ORDER BY lr.leave_date DESC, sub.slot_index ASC
    """, admin_id)
    return [dict(r) for r in rows]


@router.delete("/{leave_id}")
async def delete_leave(leave_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    row = await db.fetchrow("""
        SELECT lr.id, f.user_id FROM leave_requests lr
        JOIN faculty f ON lr.faculty_id = f.id WHERE lr.id = $1
    """, leave_id)
    if not row:
        raise HTTPException(404, "Not found")
    if user["role"] != "admin" and row["user_id"] != int(user["sub"]):
        raise HTTPException(403, "Not authorized")
    # Also delete associated substitutions
    await db.execute("DELETE FROM substitutions WHERE leave_request_id = $1", leave_id)
    await db.execute("DELETE FROM leave_requests WHERE id = $1", leave_id)
    return {"message": "Deleted"}
