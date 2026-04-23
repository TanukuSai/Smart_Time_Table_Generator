import asyncpg
import os
import json
from dotenv import load_dotenv

load_dotenv()

SUPABASE_DB_URL = os.environ.get("SUPABASE_DB_URL", "")

pool = None


async def get_db():
    async with pool.acquire() as conn:
        yield conn


async def init_db():
    global pool
    pool = await asyncpg.create_pool(SUPABASE_DB_URL, min_size=2, max_size=10, ssl="require")

    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin','faculty','student')),
                institution TEXT DEFAULT '',
                admin_id INTEGER,
                department_id INTEGER,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        # Migration columns
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS institution TEXT DEFAULT ''")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS admin_id INTEGER")
        await conn.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS department_id INTEGER")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS departments (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'UG',
                semester INTEGER NOT NULL DEFAULT 1,
                section TEXT NOT NULL,
                strength INTEGER DEFAULT 40,
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        await conn.execute("ALTER TABLE departments ADD COLUMN IF NOT EXISTS admin_id INTEGER")
        await conn.execute("ALTER TABLE departments ADD COLUMN IF NOT EXISTS level TEXT NOT NULL DEFAULT 'UG'")
        await conn.execute("ALTER TABLE departments ADD COLUMN IF NOT EXISTS room_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL")
        await conn.execute("ALTER TABLE departments ADD COLUMN IF NOT EXISTS lab_id INTEGER REFERENCES rooms(id) ON DELETE SET NULL")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
                room_id TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('classroom','lab','hall')),
                capacity INTEGER NOT NULL,
                is_available INTEGER DEFAULT 1,
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        await conn.execute("ALTER TABLE rooms ADD COLUMN IF NOT EXISTS admin_id INTEGER")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT NOT NULL,
                semester INTEGER NOT NULL DEFAULT 1,
                classes_per_week INTEGER DEFAULT 4,
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        await conn.execute("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS classes_per_week INTEGER DEFAULT 4")
        await conn.execute("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS semester INTEGER DEFAULT 1")
        await conn.execute("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS admin_id INTEGER")
        await conn.execute("ALTER TABLE subjects ADD COLUMN IF NOT EXISTS type TEXT NOT NULL DEFAULT 'theory' CHECK(type IN ('theory','lab'))")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS subject_departments (
                subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
                department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
                PRIMARY KEY (subject_id, department_id)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                employee_code TEXT NOT NULL,
                max_weekly_hours INTEGER DEFAULT 20,
                is_present INTEGER DEFAULT 1,
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        await conn.execute("ALTER TABLE faculty ADD COLUMN IF NOT EXISTS admin_id INTEGER")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS faculty_subjects (
                faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
                subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
                PRIMARY KEY (faculty_id, subject_id)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS faculty_departments (
                faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
                department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
                subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
                PRIMARY KEY (faculty_id, department_id, subject_id)
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS timetable_slots (
                id SERIAL PRIMARY KEY,
                department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
                day TEXT NOT NULL CHECK(day IN ('Mon','Tue','Wed','Thu','Fri')),
                slot_index INTEGER NOT NULL,
                slot_time TEXT NOT NULL,
                subject_id INTEGER REFERENCES subjects(id),
                faculty_id INTEGER REFERENCES faculty(id),
                room_id INTEGER REFERENCES rooms(id),
                is_break INTEGER DEFAULT 0,
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(department_id, day, slot_index)
            )
        """)

        await conn.execute("ALTER TABLE timetable_slots ADD COLUMN IF NOT EXISTS admin_id INTEGER")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS timetable_history (
                id SERIAL PRIMARY KEY,
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                generated_at TIMESTAMP DEFAULT NOW(),
                department_ids JSONB NOT NULL,
                snapshot JSONB NOT NULL,
                log TEXT,
                status TEXT NOT NULL DEFAULT 'draft',
                type TEXT NOT NULL DEFAULT 'regular',
                leave_request_id INTEGER
            )
        """)

        # Migration for existing tables
        await conn.execute("ALTER TABLE timetable_history ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'draft'")
        await conn.execute("ALTER TABLE timetable_history ADD COLUMN IF NOT EXISTS type TEXT DEFAULT 'regular'")
        await conn.execute("ALTER TABLE timetable_history ADD COLUMN IF NOT EXISTS leave_request_id INTEGER")

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leave_requests (
                id SERIAL PRIMARY KEY,
                faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
                leave_date TEXT NOT NULL,
                reason TEXT NOT NULL,
                leave_type TEXT NOT NULL DEFAULT 'casual',
                status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','denied')),
                admin_note TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                reviewed_at TIMESTAMP
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS substitutions (
                id SERIAL PRIMARY KEY,
                leave_request_id INTEGER REFERENCES leave_requests(id) ON DELETE CASCADE,
                timetable_slot_id INTEGER REFERENCES timetable_slots(id) ON DELETE CASCADE,
                original_faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
                substitute_faculty_id INTEGER REFERENCES faculty(id) ON DELETE CASCADE,
                department_id INTEGER REFERENCES departments(id) ON DELETE CASCADE,
                day TEXT NOT NULL,
                slot_index INTEGER NOT NULL,
                subject_id INTEGER REFERENCES subjects(id),
                status TEXT NOT NULL DEFAULT 'auto_assigned',
                created_at TIMESTAMP DEFAULT NOW(),
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS constraints (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('hard','soft')),
                category TEXT NOT NULL,
                is_enabled INTEGER DEFAULT 1,
                is_builtin INTEGER DEFAULT 0,
                config JSONB DEFAULT '{}',
                admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)

        await conn.execute("ALTER TABLE constraints ADD COLUMN IF NOT EXISTS admin_id INTEGER")

        await _seed_data(conn)


async def _seed_data(conn):
    user_count = await conn.fetchval("SELECT COUNT(*) FROM users")
    if user_count == 0:
        import hashlib
        def h(p): return hashlib.sha256(p.encode()).hexdigest()

        async with conn.transaction():
            # Admin user
            admin_id = await conn.fetchval(
                "INSERT INTO users (name, email, password_hash, role, institution) VALUES ($1, $2, $3, $4, $5) RETURNING id",
                "Admin User", "admin@tkrec.edu", h("admin123"), "admin", "TKREC"
            )

            # Faculty users (admin_id set to the admin)
            faculty_users = [
                ("Dr. R. Sharma", "sharma@tkrec.edu", h("faculty123"), "faculty"),
                ("Ms. P. Reddy", "reddy@tkrec.edu", h("faculty123"), "faculty"),
                ("Mr. K. Rao", "rao@tkrec.edu", h("faculty123"), "faculty"),
                ("Mrs. S. Iyer", "iyer@tkrec.edu", h("faculty123"), "faculty"),
                ("Mr. A. Verma", "verma@tkrec.edu", h("faculty123"), "faculty"),
            ]
            for name, email, pw, role in faculty_users:
                await conn.execute(
                    "INSERT INTO users (name, email, password_hash, role, admin_id) VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING",
                    name, email, pw, role, admin_id
                )

            # Departments (with admin_id)
            dept_data = [
                ("BTech-CSE-A", "UG", 1, "A", 60),
                ("BTech-CSE-B", "UG", 1, "B", 60),
                ("BTech-ECE-A", "UG", 3, "A", 50),
                ("BTech-MECH", "UG", 5, "A", 45),
                ("MTech-CS", "PG", 1, "A", 30),
            ]
            for dname, level, sem, sec, strength in dept_data:
                dept_id = await conn.fetchval(
                    "INSERT INTO departments (name, level, semester, section, strength, admin_id) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
                    dname, level, sem, sec, strength, admin_id
                )
                # Auto-create student account for this department
                stu_email = dname.lower().replace(" ", "-") + "@tkrec.edu"
                await conn.execute(
                    "INSERT INTO users (name, email, password_hash, role, admin_id, department_id) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING",
                    f"Student {dname}", stu_email, h("student123"), "student", admin_id, dept_id
                )

            # Rooms (with admin_id)
            for rid, rtype, cap in [
                ("R-101", "classroom", 60), ("R-102", "classroom", 60),
                ("R-103", "classroom", 60), ("R-104", "classroom", 60),
                ("R-105", "classroom", 60), ("Lab-1", "lab", 35),
                ("Lab-2", "lab", 35), ("Hall-A", "hall", 200),
            ]:
                await conn.execute(
                    "INSERT INTO rooms (room_id, type, capacity, admin_id) VALUES ($1, $2, $3, $4) ON CONFLICT DO NOTHING",
                    rid, rtype, cap, admin_id
                )

            # Subjects (with admin_id)
            for sname, scode, sem, cpw in [
                ("Mathematics", "MATH", 1, 5), ("Applied Maths", "AMAT", 3, 4),
                ("Physics", "PHY", 1, 4), ("Chemistry", "CHEM", 1, 4),
                ("Biology", "BIO", 5, 3), ("English", "ENG", 1, 5),
                ("Literature", "LIT", 3, 3), ("Computer Science", "CS", 1, 4),
                ("IT", "IT", 3, 3), ("Science", "SCI", 5, 3),
            ]:
                await conn.execute(
                    "INSERT INTO subjects (name, code, semester, classes_per_week, admin_id) VALUES ($1, $2, $3, $4, $5) ON CONFLICT DO NOTHING",
                    sname, scode, sem, cpw, admin_id
                )

            # Faculty records (with admin_id)
            for email, emp_code, max_hrs, is_present in [
                ("sharma@tkrec.edu", "EMP001", 20, 1),
                ("reddy@tkrec.edu", "EMP002", 18, 1),
                ("rao@tkrec.edu", "EMP003", 16, 1),
                ("iyer@tkrec.edu", "EMP004", 22, 1),
                ("verma@tkrec.edu", "EMP005", 14, 1),
            ]:
                await conn.execute("""
                    INSERT INTO faculty (user_id, employee_code, max_weekly_hours, is_present, admin_id)
                    SELECT id, $2, $3, $4, $5 FROM users WHERE email = $1
                    ON CONFLICT DO NOTHING
                """, email, emp_code, max_hrs, is_present, admin_id)

            # Faculty → Subject links
            fac_subj = [
                ("EMP001", ["MATH", "AMAT"]),
                ("EMP002", ["PHY", "SCI"]),
                ("EMP003", ["CHEM", "SCI"]),
                ("EMP004", ["ENG", "LIT"]),
                ("EMP005", ["CS", "IT"]),
            ]
            for emp, codes in fac_subj:
                for code in codes:
                    await conn.execute("""
                        INSERT INTO faculty_subjects (faculty_id, subject_id)
                        VALUES (
                            (SELECT id FROM faculty WHERE employee_code = $1),
                            (SELECT id FROM subjects WHERE code = $2 AND admin_id = $3)
                        ) ON CONFLICT DO NOTHING
                    """, emp, code, admin_id)

            # Faculty → Department → Subject assignments
            fac_dept_subj = [
                ("EMP001", "BTech-CSE-A", "MATH"), ("EMP001", "BTech-CSE-B", "MATH"),
                ("EMP001", "BTech-ECE-A", "AMAT"), ("EMP001", "BTech-MECH", "AMAT"), ("EMP001", "MTech-CS", "MATH"),
                ("EMP002", "BTech-CSE-A", "PHY"), ("EMP002", "BTech-CSE-B", "PHY"),
                ("EMP002", "BTech-ECE-A", "PHY"), ("EMP002", "BTech-MECH", "SCI"),
                ("EMP003", "BTech-CSE-A", "CHEM"), ("EMP003", "BTech-CSE-B", "SCI"),
                ("EMP003", "BTech-ECE-A", "CHEM"), ("EMP003", "BTech-MECH", "CHEM"),
                ("EMP004", "BTech-CSE-A", "ENG"), ("EMP004", "BTech-CSE-B", "ENG"),
                ("EMP004", "BTech-ECE-A", "ENG"), ("EMP004", "MTech-CS", "LIT"),
                ("EMP005", "BTech-CSE-A", "CS"), ("EMP005", "BTech-CSE-B", "CS"), ("EMP005", "MTech-CS", "IT"),
            ]
            for emp, gname, scode in fac_dept_subj:
                await conn.execute("""
                    INSERT INTO faculty_departments (faculty_id, department_id, subject_id)
                    VALUES (
                        (SELECT id FROM faculty WHERE employee_code = $1),
                        (SELECT id FROM departments WHERE name = $2 AND admin_id = $4),
                        (SELECT id FROM subjects WHERE code = $3 AND admin_id = $4)
                    ) ON CONFLICT DO NOTHING
                """, emp, gname, scode, admin_id)

            # Demo leave requests
            await conn.execute("""
                INSERT INTO leave_requests (faculty_id, leave_date, reason, leave_type, status)
                VALUES ((SELECT id FROM faculty WHERE employee_code = $1), $2, $3, $4, $5)
            """, "EMP003", "2025-07-14", "Medical appointment", "medical", "pending")
            await conn.execute("""
                INSERT INTO leave_requests (faculty_id, leave_date, reason, leave_type, status)
                VALUES ((SELECT id FROM faculty WHERE employee_code = $1), $2, $3, $4, $5)
            """, "EMP002", "2025-07-16", "Family function", "casual", "pending")

            # Built-in constraints (per admin)
            for name, ctype, category in [
                ("No faculty double-booking", "hard", "no_faculty_double_booking"),
                ("No room double-booking", "hard", "no_room_double_booking"),
                ("Respect max weekly hours", "hard", "respect_max_weekly_hours"),
                ("Balance faculty workload", "soft", "balance_workload"),
            ]:
                await conn.execute("""
                    INSERT INTO constraints (name, type, category, is_enabled, is_builtin, config, admin_id)
                    VALUES ($1, $2, $3, 1, 1, $4::jsonb, $5)
                """, name, ctype, category, json.dumps({}), admin_id)


async def close_db():
    global pool
    if pool:
        await pool.close()
