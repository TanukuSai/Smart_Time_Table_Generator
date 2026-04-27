from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
from routers.auth import get_current_user, require_admin, get_admin_id
import random
import json
from datetime import datetime, timedelta, date

router = APIRouter()

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
ALL_TIMES = [
    "8:00–8:45", "8:45–9:30", "9:30–10:15",
    "10:30–11:15", "11:15–12:00", "12:00–12:45", "12:45–1:30"
]
BREAK_SLOT = 3

class GenerateRequest(BaseModel):
    department_ids: List[int]
    slots_per_day: int = 6
    start_time: str = "08:00"
    class_duration: int = 45
    break_duration: int = 45
    working_days: int = 6

class SlotEditRequest(BaseModel):
    department_name: str
    day: str
    slot_index: int
    faculty_name: Optional[str] = None
    subject_name: Optional[str] = None
    faculty_id: Optional[int] = None
    subject_id: Optional[int] = None

# ──────────────── History endpoints ────────────────

@router.get("/history")
async def get_history(db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    rows = await db.fetch(
        "SELECT id, name, generated_at, department_ids, log, status, type, leave_request_id FROM timetable_history WHERE admin_id = $1 ORDER BY generated_at DESC",
        admin_id
    )
    return [dict(r) for r in rows]

@router.get("/history/{history_id}")
async def get_history_detail(history_id: int, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    row = await db.fetchrow(
        "SELECT * FROM timetable_history WHERE id = $1 AND admin_id = $2",
        history_id, admin_id
    )
    if not row:
        raise HTTPException(404, "History entry not found")
    return dict(row)

@router.delete("/history/{history_id}")
async def delete_history(history_id: int, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    row = await db.fetchrow("SELECT id FROM timetable_history WHERE id = $1 AND admin_id = $2", history_id, admin_id)
    if not row:
        raise HTTPException(404, "History entry not found")
    await db.execute("DELETE FROM timetable_history WHERE id = $1", history_id)
    return {"message": "Deleted"}

# ──────────────── Publish a draft ────────────────

@router.post("/history/{history_id}/publish")
async def publish_timetable(history_id: int, db=Depends(get_db), user=Depends(require_admin)):
    """Publish a draft timetable: write snapshot to timetable_slots and mark as published."""
    admin_id = get_admin_id(user)
    row = await db.fetchrow(
        "SELECT * FROM timetable_history WHERE id = $1 AND admin_id = $2",
        history_id, admin_id
    )
    if not row:
        raise HTTPException(404, "History entry not found")
    if row["status"] == "published":
        raise HTTPException(400, "Already published")

    snapshot = row["snapshot"] if isinstance(row["snapshot"], dict) else json.loads(row["snapshot"])
    dept_ids = row["department_ids"] if isinstance(row["department_ids"], list) else json.loads(row["department_ids"])

    async with db.transaction():
        if row["type"] == "regular":
            # Archive previously published regular timetables
            await db.execute(
                "UPDATE timetable_history SET status = 'archived' WHERE admin_id = $1 AND type = 'regular' AND status = 'published'",
                admin_id
            )

            # Clear existing live slots for these departments
            for dept_id in dept_ids:
                await db.execute("DELETE FROM timetable_slots WHERE department_id = $1 AND admin_id = $2", dept_id, admin_id)

            # Write snapshot to live timetable_slots
            # We need department name → id mapping
            dept_map = {}
            for dept_id in dept_ids:
                dept = await db.fetchrow("SELECT id, name FROM departments WHERE id = $1", dept_id)
                if dept:
                    dept_map[dept["name"]] = dept["id"]

            # Also build name-based lookups for faculty and subjects
            faculty_rows = await db.fetch("""
                SELECT f.id, u.name FROM faculty f JOIN users u ON f.user_id = u.id WHERE f.admin_id = $1
            """, admin_id)
            faculty_name_map = {r["name"]: r["id"] for r in faculty_rows}

            subject_rows = await db.fetch("SELECT id, name FROM subjects WHERE admin_id = $1", admin_id)
            subject_name_map = {r["name"]: r["id"] for r in subject_rows}

            room_rows = await db.fetch("SELECT id, room_id FROM rooms WHERE admin_id = $1", admin_id)
            room_ids = [r["id"] for r in room_rows]

            room_idx = 0
            for dept_name, days_data in snapshot.items():
                dept_id = dept_map.get(dept_name)
                if not dept_id:
                    continue
                for day, slots in days_data.items():
                    for slot in slots:
                        slot_idx = slot["slot_index"]
                        slot_time = slot.get("slot_time", "")
                        is_break = slot.get("is_break", 0)
                        subject_name = slot.get("subject")
                        faculty_name = slot.get("faculty")

                        subject_id = subject_name_map.get(subject_name) if subject_name else None
                        faculty_id = faculty_name_map.get(faculty_name) if faculty_name else None
                        room_id = room_ids[room_idx % len(room_ids)] if room_ids and not is_break and subject_id else None
                        if not is_break and subject_id:
                            room_idx += 1

                        await db.execute("""
                            INSERT INTO timetable_slots
                            (department_id, day, slot_index, slot_time, subject_id, faculty_id, room_id, is_break, admin_id)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                        """, dept_id, day, slot_idx, slot_time, subject_id, faculty_id, room_id, is_break, admin_id)

        elif row["type"] == "substitution":
            # For substitutions, we just apply any edits from the snapshot to the substitutions table
            leave_request_id = row.get("leave_request_id")
            if leave_request_id:
                # Find the faculty ID lookup
                faculty_rows = await db.fetch("SELECT f.id, u.name FROM faculty f JOIN users u ON f.user_id = u.id WHERE f.admin_id = $1", admin_id)
                faculty_name_map = {r["name"]: r["id"] for r in faculty_rows}
                
                # Fetch departments lookup
                dept_map = {}
                for dept_id in dept_ids:
                    dept = await db.fetchrow("SELECT id, name FROM departments WHERE id = $1", dept_id)
                    if dept:
                        dept_map[dept["name"]] = dept["id"]

                for dept_name, days_data in snapshot.items():
                    dept_id = dept_map.get(dept_name)
                    if not dept_id:
                        continue
                    for day, slots in days_data.items():
                        for slot in slots:
                            if not slot.get("is_substitution"):
                                continue
                            slot_idx = slot["slot_index"]
                            faculty_name = slot.get("faculty")
                            faculty_id = faculty_name_map.get(faculty_name) if faculty_name else None
                            
                            # Update the substitutions table
                            await db.execute("""
                                UPDATE substitutions 
                                SET substitute_faculty_id = $1 
                                WHERE leave_request_id = $2 AND department_id = $3 AND day = $4 AND slot_index = $5
                            """, faculty_id, leave_request_id, dept_id, day, slot_idx)

        # Mark as published
        await db.execute("UPDATE timetable_history SET status = 'published' WHERE id = $1", history_id)

    return {"message": "Timetable published and now live"}

# ──────────────── Edit a draft slot ────────────────

@router.patch("/history/{history_id}/slot")
async def edit_draft_slot(history_id: int, body: SlotEditRequest, db=Depends(get_db), user=Depends(require_admin)):
    """Edit a single slot in a draft snapshot before publishing."""
    admin_id = get_admin_id(user)
    row = await db.fetchrow(
        "SELECT * FROM timetable_history WHERE id = $1 AND admin_id = $2",
        history_id, admin_id
    )
    if not row:
        raise HTTPException(404, "History entry not found")
    if row["status"] == "published":
        raise HTTPException(400, "Cannot edit a published timetable")

    snapshot = row["snapshot"] if isinstance(row["snapshot"], dict) else json.loads(row["snapshot"])

    dept_data = snapshot.get(body.department_name)
    if not dept_data:
        raise HTTPException(404, f"Department '{body.department_name}' not found in snapshot")

    day_slots = dept_data.get(body.day)
    if not day_slots:
        raise HTTPException(404, f"Day '{body.day}' not found")

    # Find the slot by index
    found = False
    for slot in day_slots:
        if slot["slot_index"] == body.slot_index:
            # Resolve names from IDs if provided
            if body.faculty_id:
                fac = await db.fetchrow("SELECT u.name FROM faculty f JOIN users u ON f.user_id = u.id WHERE f.id = $1", body.faculty_id)
                if fac:
                    slot["faculty"] = fac["name"]
            elif body.faculty_name is not None:
                slot["faculty"] = body.faculty_name or None

            if body.subject_id:
                subj = await db.fetchrow("SELECT name FROM subjects WHERE id = $1", body.subject_id)
                if subj:
                    slot["subject"] = subj["name"]
            elif body.subject_name is not None:
                slot["subject"] = body.subject_name or None

            found = True
            break

    if not found:
        raise HTTPException(404, f"Slot index {body.slot_index} not found")

    await db.execute(
        "UPDATE timetable_history SET snapshot = $1::jsonb WHERE id = $2",
        json.dumps(snapshot), history_id
    )
    return {"message": "Slot updated", "snapshot": snapshot}

# ──────────────── Live timetable with substitution overlay ────────────────

async def _get_active_substitutions(db, admin_id: int, department_ids: list = None, client_date_str: str = None):
    """Get active substitutions, filtered by time window."""
    from datetime import date, timedelta, datetime
    
    if client_date_str:
        try:
            today = datetime.strptime(client_date_str, "%Y-%m-%d").date()
        except ValueError:
            today = date.today()
    else:
        today = date.today()
        
    tomorrow = today + timedelta(days=1)
    today_str = today.isoformat()
    tomorrow_str = tomorrow.isoformat()

    base_query = """
        SELECT sub.day, sub.slot_index, sub.department_id, sub.subject_id,
               sub.original_faculty_id, sub.substitute_faculty_id,
               u_orig.name as original_faculty_name,
               u_sub.name as substitute_faculty_name,
               s.name as subject_name,
               lr.leave_date
        FROM substitutions sub
        JOIN leave_requests lr ON sub.leave_request_id = lr.id
        LEFT JOIN faculty f_orig ON sub.original_faculty_id = f_orig.id
        LEFT JOIN users u_orig ON f_orig.user_id = u_orig.id
        LEFT JOIN faculty f_sub ON sub.substitute_faculty_id = f_sub.id
        LEFT JOIN users u_sub ON f_sub.user_id = u_sub.id
        LEFT JOIN subjects s ON sub.subject_id = s.id
        WHERE sub.admin_id = $1 AND lr.status = 'approved' AND sub.status IN ('auto_assigned', 'no_substitute', 'manually_assigned')
    """
    params = [admin_id]

    if department_ids:
        params.append(department_ids)
        base_query += f" AND sub.department_id = ANY(${len(params)}::int[])"

    # Time window: only show on the day before and day of leave
    params.append(today_str)
    params.append(tomorrow_str)
    base_query += f" AND lr.leave_date IN (${len(params)-1}, ${len(params)})"

    rows = await db.fetch(base_query, *params)
    return rows


@router.get("/{department_id}")
async def get_timetable(department_id: int, db=Depends(get_db), user=Depends(get_current_user), date: Optional[str] = None):
    admin_id = get_admin_id(user)
    dept = await db.fetchrow("SELECT id FROM departments WHERE id = $1 AND admin_id = $2", department_id, admin_id)
    if not dept:
        raise HTTPException(404, "Department not found")

    rows = await db.fetch("""
        SELECT ts.id, ts.day, ts.slot_index, ts.slot_time, ts.is_break,
               s.name as subject_name, s.code as subject_code,
               u.name as faculty_name, f.id as faculty_id,
               r.room_id as room_name
        FROM timetable_slots ts
        LEFT JOIN subjects s ON ts.subject_id = s.id
        LEFT JOIN faculty f ON ts.faculty_id = f.id
        LEFT JOIN users u ON f.user_id = u.id
        LEFT JOIN rooms r ON ts.room_id = r.id
        WHERE ts.department_id = $1 AND ts.admin_id = $2
        ORDER BY ts.day, ts.slot_index
    """, department_id, admin_id)

    # Get active substitutions
    subs = await _get_active_substitutions(db, admin_id, [department_id], client_date_str=date)
    sub_map = {}  # (day, slot_index) → substitution data
    for s in subs:
        sub_map[(s["day"], s["slot_index"])] = s

    result = {}
    for r in rows:
        d = r["day"]
        if d not in result:
            result[d] = []
        slot = dict(r)
        # Overlay substitution if present
        key = (d, r["slot_index"])
        if key in sub_map:
            sub = sub_map[key]
            slot["is_substituted"] = True
            slot["original_faculty_name"] = sub["original_faculty_name"]
            slot["substitute_faculty_name"] = sub["substitute_faculty_name"]
            slot["faculty_name"] = sub["substitute_faculty_name"] or "TBD"
        result[d].append(slot)
    return result

@router.get("")
async def get_all_timetables(db=Depends(get_db), user=Depends(get_current_user), date: Optional[str] = None):
    admin_id = get_admin_id(user)

    # For students, only return their department's timetable
    if user["role"] == "student":
        dept_id = user.get("department_id")
        if not dept_id:
            return {}
        dept = await db.fetchrow("SELECT * FROM departments WHERE id = $1 AND admin_id = $2", int(dept_id), admin_id)
        if not dept:
            return {}
            
        same_name_depts = await db.fetch("SELECT id FROM departments WHERE name = $1 AND admin_id = $2", dept["name"], admin_id)
        dept_ids = [r["id"] for r in same_name_depts]

        rows = await db.fetch("""
            SELECT ts.day, ts.slot_index, ts.slot_time, ts.is_break,
                   s.name as subject_name, u.name as faculty_name, r.room_id as room_name
            FROM timetable_slots ts
            LEFT JOIN subjects s ON ts.subject_id = s.id
            LEFT JOIN faculty f ON ts.faculty_id = f.id
            LEFT JOIN users u ON f.user_id = u.id
            LEFT JOIN rooms r ON ts.room_id = r.id
            WHERE ts.department_id = ANY($1::int[]) AND ts.admin_id = $2
            ORDER BY ts.day, ts.slot_index
        """, dept_ids, admin_id)

        # Get substitution overlay
        subs = await _get_active_substitutions(db, admin_id, dept_ids, client_date_str=date)
        sub_map = {(s["day"], s["slot_index"]): s for s in subs}

        if rows:
            days = {}
            for row in rows:
                day = row["day"]
                if day not in days:
                    days[day] = []
                slot = dict(row)
                key = (day, row["slot_index"])
                if key in sub_map:
                    sub = sub_map[key]
                    slot["is_substituted"] = True
                    slot["original_faculty_name"] = sub["original_faculty_name"]
                    slot["substitute_faculty_name"] = sub["substitute_faculty_name"]
                    slot["faculty_name"] = sub["substitute_faculty_name"] or "TBD"
                days[day].append(slot)
            return {dept["name"]: {"department_id": dept["id"], "days": days}}
        return {}

    departments = await db.fetch("SELECT * FROM departments WHERE admin_id = $1 ORDER BY name", admin_id)
    result = {}
    for g in departments:
        rows = await db.fetch("""
            SELECT ts.day, ts.slot_index, ts.slot_time, ts.is_break,
                   s.name as subject_name, u.name as faculty_name, r.room_id as room_name
            FROM timetable_slots ts
            LEFT JOIN subjects s ON ts.subject_id = s.id
            LEFT JOIN faculty f ON ts.faculty_id = f.id
            LEFT JOIN users u ON f.user_id = u.id
            LEFT JOIN rooms r ON ts.room_id = r.id
            WHERE ts.department_id = $1 AND ts.admin_id = $2
            ORDER BY ts.day, ts.slot_index
        """, g["id"], admin_id)
        if rows:
            # Get substitution overlay
            subs = await _get_active_substitutions(db, admin_id, [g["id"]], client_date_str=date)
            sub_map = {(s["day"], s["slot_index"]): s for s in subs}

            days = {}
            for row in rows:
                day = row["day"]
                if day not in days:
                    days[day] = []
                slot = dict(row)
                key = (day, row["slot_index"])
                if key in sub_map:
                    sub = sub_map[key]
                    slot["is_substituted"] = True
                    slot["original_faculty_name"] = sub["original_faculty_name"]
                    slot["substitute_faculty_name"] = sub["substitute_faculty_name"]
                    slot["faculty_name"] = sub["substitute_faculty_name"] or "TBD"
                days[day].append(slot)
            result[g["name"]] = {"department_id": g["id"], "days": days}
    return result

# ──────────────── Generate (saves as DRAFT only) ────────────────

@router.post("/generate")
async def generate_timetable(body: GenerateRequest, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    log = []
    log.append("[CSP] Initializing constraint satisfaction engine...")

    TIMES = []
    LOCAL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][:body.working_days]
    break_slot_idx = body.slots_per_day // 2
    
    start_dt = datetime.strptime(body.start_time, "%H:%M")
    current_time = start_dt
    for i in range(body.slots_per_day + 1):
        if i == break_slot_idx:
            end_time = current_time + timedelta(minutes=body.break_duration)
            TIMES.append(f"{current_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}")
            current_time = end_time
        else:
            end_time = current_time + timedelta(minutes=body.class_duration)
            TIMES.append(f"{current_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}")
            current_time = end_time

    # ---------- Load all enabled constraints for this admin ----------
    constraint_rows = await db.fetch("SELECT * FROM constraints WHERE is_enabled = 1 AND admin_id = $1", admin_id)
    active_constraints = {}
    for r in constraint_rows:
        active_constraints[r["category"]] = dict(r)
    log.append(f"[CSP] Loaded {len(active_constraints)} active constraints")

    # ---------- Load rooms for this admin ----------
    rooms = await db.fetch("SELECT id, type FROM rooms WHERE is_available = 1 AND admin_id = $1", admin_id)
    room_ids = [r["id"] for r in rooms]
    lab_room_ids = [r["id"] for r in rooms if r["type"] == "lab"]
    if not room_ids:
        raise HTTPException(400, "No available rooms — add rooms first")

    # ---------- Parse custom constraint configs ----------
    custom_rows = await db.fetch("SELECT * FROM constraints WHERE is_enabled = 1 AND is_builtin = 0 AND admin_id = $1", admin_id)

    faculty_unavailable = {}
    faculty_max_per_day_map = {}
    subject_max_per_day_map = {}
    no_consecutive_subjects = set()
    subject_preferred_slots = {}

    for c in custom_rows:
        cfg = c["config"] if isinstance(c["config"], dict) else json.loads(c["config"]) if c["config"] else {}
        cat = c["category"]

        if cat == "faculty_unavailable_slot":
            fid = cfg.get("faculty_id")
            day = cfg.get("day")
            slot = cfg.get("slot_index")
            if fid is not None and day and slot is not None:
                faculty_unavailable.setdefault(int(fid), set()).add((day, int(slot)))
        elif cat == "faculty_max_per_day":
            fid = cfg.get("faculty_id")
            mx = cfg.get("max", 99)
            if fid is not None:
                faculty_max_per_day_map[int(fid)] = int(mx)
        elif cat == "max_subject_per_day":
            sid = cfg.get("subject_id")
            mx = cfg.get("max", 99)
            if sid is not None:
                subject_max_per_day_map[int(sid)] = int(mx)
        elif cat == "no_consecutive_same_subject":
            sid = cfg.get("subject_id")
            if sid is not None:
                no_consecutive_subjects.add(int(sid))
        elif cat == "subject_preferred_slot":
            sid = cfg.get("subject_id")
            slots = cfg.get("slots", [])
            if sid is not None and slots:
                subject_preferred_slots[int(sid)] = set(int(s) for s in slots)

    # ---------- GLOBAL tracking (across all departments) ----------
    global_faculty_slots = {}
    global_room_slots = {}
    global_faculty_hours = {}

    # ---------- Build snapshot for history ----------
    snapshot = {}
    dept_names = []

    # ---------- Generate for each department ----------
    for department_id in body.department_ids:
        department = await db.fetchrow("SELECT name, room_id, lab_id FROM departments WHERE id = $1 AND admin_id = $2", department_id, admin_id)
        if not department:
            continue
        gname = department["name"]
        dept_room_id = department["room_id"]
        dept_lab_id = department["lab_id"]
        dept_names.append(gname)
        log.append(f"\n[CSP] ── Processing department {gname} ──")

        assignments = await db.fetch("""
            SELECT fg.faculty_id, fg.subject_id, f.max_weekly_hours,
                   u.name as faculty_name, s.name as subject_name,
                   s.classes_per_week, s.type as subject_type
            FROM faculty_departments fg
            JOIN faculty f ON fg.faculty_id = f.id
            JOIN users u ON f.user_id = u.id
            JOIN subjects s ON fg.subject_id = s.id
            WHERE fg.department_id = $1 AND f.is_present = 1 AND f.admin_id = $2
        """, department_id, admin_id)

        if not assignments:
            log.append(f"[CSP]   No available faculty for {gname}, skipping.")
            continue

        subject_target = {}
        for a in assignments:
            sid = a["subject_id"]
            if sid not in subject_target:
                subject_target[sid] = a["classes_per_week"] or 4

        subject_count = {}
        faculty_day_count = {}
        subject_day_count = {}
        grade_schedule = {}
        dept_snapshot = {}
        
        lab_assignments = [a for a in assignments if a["subject_type"] == "lab"]
        theory_assignments = [a for a in assignments if a["subject_type"] == "theory"]

        # Track pre-scheduled slots for this department: (day, slot_idx) -> assignment
        dept_pre_scheduled = {}

        # PRE-SCHEDULE LABS
        for a in lab_assignments:
            fid = a["faculty_id"]
            sid = a["subject_id"]
            n_classes = a["classes_per_week"] or 2
            if n_classes > 3:
                raise HTTPException(400, f"Cannot generate timetable: Lab subject '{a['subject_name']}' requires {n_classes} hours per week, but labs cannot exceed 3 hours.")
                
            if not dept_lab_id:
                log.append(f"[CSP]   ✗ {gname} has no base lab assigned. Cannot schedule lab {a['subject_name']}.")
                continue

            scheduled = False
            days_shuffled = list(LOCAL_DAYS)
            random.shuffle(days_shuffled)
            
            for day in days_shuffled:
                before_break = tuple(range(0, break_slot_idx))
                after_break = tuple(range(break_slot_idx + 1, len(TIMES)))
                sessions = [before_break, after_break]
                random.shuffle(sessions)
                
                for session in sessions:
                    valid_starts = [i for i in range(len(session) - n_classes + 1)]
                    random.shuffle(valid_starts)
                    
                    for start_idx in valid_starts:
                        block_slots = [session[start_idx + i] for i in range(n_classes)]
                        
                        available = True
                        for s_idx in block_slots:
                            if (day, s_idx) in dept_pre_scheduled:
                                available = False
                                break
                            if "no_faculty_double_booking" in active_constraints:
                                if (day, s_idx) in global_faculty_slots.get(fid, set()):
                                    available = False
                                    break
                            if fid in faculty_unavailable and (day, s_idx) in faculty_unavailable[fid]:
                                available = False
                                break
                            if "no_room_double_booking" in active_constraints:
                                if (day, s_idx) in global_room_slots.get(dept_lab_id, set()):
                                    available = False
                                    break
                                    
                        if available:
                            for s_idx in block_slots:
                                global_faculty_slots.setdefault(fid, set()).add((day, s_idx))
                                global_room_slots.setdefault(dept_lab_id, set()).add((day, s_idx))
                                global_faculty_hours[fid] = global_faculty_hours.get(fid, 0) + 1
                                subject_count[sid] = subject_count.get(sid, 0) + 1
                                faculty_day_count[(fid, day)] = faculty_day_count.get((fid, day), 0) + 1
                                subject_day_count[(sid, day)] = subject_day_count.get((sid, day), 0) + 1
                                grade_schedule[(day, s_idx)] = (fid, sid)
                                dept_pre_scheduled[(day, s_idx)] = a
                                
                            log.append(f"[CSP]   ✓ {day} slots {block_slots}: Lab {a['subject_name']} ({n_classes}h block) → {a['faculty_name']} in Lab {dept_lab_id}")
                            scheduled = True
                            break
                    if scheduled: break
                if scheduled: break
                    
            if not scheduled:
                log.append(f"[CSP]   ✗ Could not find a contiguous {n_classes}h block for Lab {a['subject_name']} in Lab {dept_lab_id}")

        # SCHEDULE THEORY
        for day in LOCAL_DAYS:
            for slot_idx in range(len(TIMES)):
                if slot_idx == break_slot_idx:
                    dept_snapshot.setdefault(day, []).append({
                        "slot_index": slot_idx, "slot_time": TIMES[slot_idx], "is_break": 1
                    })
                    continue
                
                if (day, slot_idx) in dept_pre_scheduled:
                    a = dept_pre_scheduled[(day, slot_idx)]
                    dept_snapshot.setdefault(day, []).append({
                        "slot_index": slot_idx, "slot_time": TIMES[slot_idx],
                        "subject": a["subject_name"], "faculty": a["faculty_name"],
                        "is_break": 0
                    })
                    continue

                candidates = list(theory_assignments)
                random.shuffle(candidates)
                do_balance = "balance_workload" in active_constraints

                def priority(a):
                    sid = a["subject_id"]
                    fid = a["faculty_id"]
                    cur = subject_count.get(sid, 0)
                    tgt = subject_target.get(sid, 4)
                    sub_ratio = cur / max(tgt, 1)
                    fac_ratio = (global_faculty_hours.get(fid, 0) / max(a["max_weekly_hours"], 1)) if do_balance else 0
                    return (sub_ratio, fac_ratio)

                candidates.sort(key=priority)

                assigned = False
                for a in candidates:
                    fid = a["faculty_id"]
                    sid = a["subject_id"]

                    if "no_faculty_double_booking" in active_constraints:
                        if (day, slot_idx) in global_faculty_slots.get(fid, set()):
                            log.append(f"[CSP]   ✗ {a['faculty_name']} double-booked at {day} slot {slot_idx}")
                            continue

                    if "respect_max_weekly_hours" in active_constraints:
                        if global_faculty_hours.get(fid, 0) >= a["max_weekly_hours"]:
                            continue

                    if fid in faculty_unavailable:
                        if (day, slot_idx) in faculty_unavailable[fid]:
                            log.append(f"[CSP]   ✗ {a['faculty_name']} unavailable at {day} slot {slot_idx}")
                            continue

                    if fid in faculty_max_per_day_map:
                        if faculty_day_count.get((fid, day), 0) >= faculty_max_per_day_map[fid]:
                            continue

                    if sid in subject_max_per_day_map:
                        if subject_day_count.get((sid, day), 0) >= subject_max_per_day_map[sid]:
                            continue

                    if subject_count.get(sid, 0) >= subject_target.get(sid, 4):
                        continue

                    if sid in no_consecutive_subjects and slot_idx > 0:
                        prev = grade_schedule.get((day, slot_idx - 1))
                        if prev and prev[1] == sid:
                            continue

                    if sid in subject_preferred_slots:
                        if slot_idx not in subject_preferred_slots[sid]:
                            continue

                    # Room assignment (draft only)
                    room_id = dept_room_id
                    if room_id is None:
                        log.append(f"[CSP]   ✗ {gname} has no base classroom assigned. Cannot schedule theory {a['subject_name']}.")
                        continue
                    if "no_room_double_booking" in active_constraints:
                        if (day, slot_idx) in global_room_slots.get(room_id, set()):
                            log.append(f"[CSP]   ✗ Base Classroom {room_id} double-booked (likely shared incorrectly)")
                            continue

                    # ═══ ASSIGN (to snapshot only, NOT to timetable_slots) ═══
                    global_faculty_slots.setdefault(fid, set()).add((day, slot_idx))
                    global_room_slots.setdefault(room_id, set()).add((day, slot_idx))
                    global_faculty_hours[fid] = global_faculty_hours.get(fid, 0) + 1
                    subject_count[sid] = subject_count.get(sid, 0) + 1
                    faculty_day_count[(fid, day)] = faculty_day_count.get((fid, day), 0) + 1
                    subject_day_count[(sid, day)] = subject_day_count.get((sid, day), 0) + 1
                    grade_schedule[(day, slot_idx)] = (fid, sid)

                    dept_snapshot.setdefault(day, []).append({
                        "slot_index": slot_idx, "slot_time": TIMES[slot_idx],
                        "subject": a["subject_name"], "faculty": a["faculty_name"],
                        "is_break": 0
                    })

                    log.append(f"[CSP]   ✓ {day} slot {slot_idx}: {a['subject_name']} → {a['faculty_name']}")
                    assigned = True
                    break

                if not assigned:
                    dept_snapshot.setdefault(day, []).append({
                        "slot_index": slot_idx, "slot_time": TIMES[slot_idx],
                        "is_break": 0, "subject": None, "faculty": None
                    })
                    log.append(f"[CSP]   ○ {day} slot {slot_idx}: No valid assignment, left empty")

        snapshot[gname] = dept_snapshot
        log.append(f"[CSP] ── Department {gname} complete ──")

    # ---------- Summary ----------
    total_conflicts = sum(1 for line in log if "double-booked" in line)
    log.append(f"\n[DONE] Generation complete. {total_conflicts} cross-department conflicts resolved.")
    log.append(f"[DONE] All constraints enforced globally across {len(body.department_ids)} departments.")
    log.append(f"[DRAFT] Saved as draft — review and publish from History page.")

    # ---------- Save as DRAFT to history (NOT to timetable_slots) ----------
    history_name = f"Generation — {', '.join(dept_names[:3])}{'...' if len(dept_names) > 3 else ''}"
    log_text = "\n".join(log)
    history_id = await db.fetchval("""
        INSERT INTO timetable_history (admin_id, name, department_ids, snapshot, log, status, type)
        VALUES ($1, $2, $3::jsonb, $4::jsonb, $5, 'draft', 'regular')
        RETURNING id
    """, admin_id, history_name, json.dumps(body.department_ids), json.dumps(snapshot), log_text)

    return {"log": log, "message": "Timetable generated as draft — review and publish from History", "history_id": history_id}

@router.put("/{slot_id}")
async def update_slot(slot_id: int, faculty_id: Optional[int] = None,
                      room_id: Optional[int] = None, db=Depends(get_db), user=Depends(require_admin)):
    admin_id = get_admin_id(user)
    existing = await db.fetchrow("SELECT id FROM timetable_slots WHERE id = $1 AND admin_id = $2", slot_id, admin_id)
    if not existing:
        raise HTTPException(404, "Slot not found")
    if faculty_id is not None:
        await db.execute("UPDATE timetable_slots SET faculty_id = $1 WHERE id = $2", faculty_id, slot_id)
    if room_id is not None:
        await db.execute("UPDATE timetable_slots SET room_id = $1 WHERE id = $2", room_id, slot_id)
    return {"message": "Slot updated"}
