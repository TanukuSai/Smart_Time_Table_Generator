# STTG — Smart Time Table Generator
**Teegala Krishna Reddy Engineering College**

A full-stack web application for automated, constraint-based academic scheduling with role-based access for Admins, Faculty, and Students.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite, React Router, Axios, Lucide icons |
| Backend | Python FastAPI + Uvicorn |
| Database | SQLite via aiosqlite (drop-in swap to PostgreSQL) |
| Auth | JWT (PyJWT), SHA-256 password hashing |
| Styling | Pure CSS with CSS Variables, Syne + DM Sans fonts |

---

## Project Structure

```
sttg/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # DB init, schema, seed data
│   ├── auth_utils.py        # JWT + password helpers
│   ├── requirements.txt
│   └── routers/
│       ├── auth.py          # Login, token validation
│       ├── faculty.py       # Faculty CRUD + schedule
│       ├── rooms.py         # Room management
│       ├── grades.py        # Grades + subjects
│       ├── timetable.py     # Timetable view + CSP generator
│       └── leaves.py        # Leave request + review
└── frontend/
    ├── index.html
    ├── vite.config.js
    ├── package.json
    └── src/
        ├── App.jsx           # Router + role-based routing
        ├── index.css         # Global design system
        ├── main.jsx
        ├── context/
        │   └── AuthContext.jsx
        ├── utils/
        │   └── api.js        # Axios instance
        ├── components/
        │   ├── Layout.jsx    # Sidebar + nav shell
        │   └── TimetableGrid.jsx
        └── pages/
            ├── LoginPage.jsx
            ├── admin/        Dashboard, Faculty, Rooms, Leaves, Generate
            ├── faculty/      Dashboard, Schedule, Leave
            ├── student/      Timetable, FacultyToday
            └── shared/       TimetablePage
```

---

## Setup & Running

### 1. Backend

```bash
cd backend

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server (DB auto-creates and seeds on first run)
python main.py
# → API running at http://localhost:8000
# → Docs at http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → App running at http://localhost:5173
```

---

## Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@tkrec.edu | admin123 |
| Faculty (Dr. Sharma) | sharma@tkrec.edu | faculty123 |
| Faculty (Ms. Reddy) | reddy@tkrec.edu | faculty123 |
| Faculty (Mr. Rao) | rao@tkrec.edu | faculty123 |
| Student | student@tkrec.edu | student123 |

---

## Role Capabilities

### Admin
- Dashboard with live alerts (absent faculty, pending leaves, metrics)
- Full timetable view per grade
- Add / remove faculty with **multiple subjects** and **multiple grade assignments** (e.g. Dr. Sharma teaches Maths to 10A and Applied Maths to 11A)
- Manage rooms and labs
- Approve or deny faculty leave requests with optional admin note
- Run the **CSP timetable generator** — select grades, configure constraints, view live algorithm log

### Faculty
- Personal dashboard showing today's classes
- Weekly calendar view with only their assigned slots
- Submit leave requests (casual, medical, conference, emergency)
- View leave history with admin response notes

### Student
- Read-only timetable view per grade
- See which faculty are present / absent today with their subjects and assigned grades

---

## Database Schema Highlights

The relational model is designed to handle the M:M:M relationship between Faculty, Subjects, and Grades:

- `faculty_subjects` — which subjects a faculty member is qualified to teach
- `faculty_grades` — which subject a faculty member teaches to a specific grade (one teacher can teach *different* subjects to different grades)
- `timetable_slots` — each row is one period: grade + day + slot index → subject + faculty + room

---

## CSP Algorithm

The `POST /api/timetable/generate` endpoint implements a backtracking Constraint Satisfaction Problem solver:

1. **Variables**: each (grade, day, slot) combination
2. **Domain**: all faculty-grade-subject assignments for that grade
3. **Hard constraints** (always enforced):
   - No faculty double-booking in the same timeslot
   - Faculty not assigned beyond their `max_weekly_hours`
4. **Soft constraints** (configurable):
   - Balance workload across faculty
5. **Backtracking**: if a conflict is detected, the solver tries the next available assignment

---

## Switching to PostgreSQL

In `database.py`, replace `aiosqlite.connect(DB_PATH)` with `asyncpg` and set your connection string. All SQL is standard and compatible. Add `asyncpg` to `requirements.txt` and update the connection factory in `database.py`.
