# STTG — Smart Time Table Generator

A full-stack web application for automated, constraint-based academic scheduling with role-based access for Admins, Faculty, and Students.

Built for **Teegala Krishna Reddy Engineering College**.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18 + Vite, React Router, Axios, Lucide Icons |
| Backend | Python FastAPI + Uvicorn |
| Database | PostgreSQL (Supabase) / SQLite (aiosqlite) |
| Auth | JWT (PyJWT), SHA-256 password hashing |
| Styling | Pure CSS with CSS Variables, Syne + DM Sans fonts |
| Algorithm | CSP with Backtracking + AC-3 arc consistency |

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
│       ├── subjects.py      # Subject management
│       ├── departments.py   # Department management
│       ├── constraints.py   # Scheduling constraints
│       ├── timetable.py     # Timetable view + CSP generator
│       └── leaves.py        # Leave request + substitution
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
            ├── admin/        # Dashboard, Faculty, Rooms, Subjects, Departments, Constraints, Generate, History, Leaves
            ├── faculty/      # Dashboard, Schedule, Leave
            ├── student/      # Timetable, FacultyToday
            └── shared/       # TimetablePage
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

## Key Features

### Admin
- Dashboard with live alerts (absent faculty, pending leaves, metrics)
- Full timetable view per department
- Manage faculty with **multiple subjects** and **multiple department assignments**
- Manage rooms, labs, subjects, and departments
- Configure **hard and soft scheduling constraints** (built-in + custom)
- Approve or deny faculty leave requests with optional admin notes
- Run the **CSP timetable generator** — select departments, configure slots/days/timings, view live algorithm log
- Full timetable **history** with draft and published states

### Faculty
- Personal dashboard showing today's classes and substitution duties
- Weekly calendar view with only their assigned slots
- Submit leave requests (casual, medical, emergency)
- View leave history with admin response notes

### Student
- Read-only timetable view for their department
- See which faculty are present / absent today with their subjects

---

## CSP Algorithm

The `POST /api/timetable/generate` endpoint implements a backtracking Constraint Satisfaction Problem solver:

1. **Variables**: each (department, day, slot) combination
2. **Domain**: all faculty-department-subject assignments for that department
3. **Hard constraints** (always enforced):
   - No faculty double-booking in the same timeslot
   - No room double-booking
   - Faculty not assigned beyond their `max_weekly_hours`
   - Strict base classroom/lab routing
   - Contiguous lab blocks
4. **Soft constraints** (configurable):
   - Balance workload across faculty
5. **Backtracking**: if a conflict is detected, the solver tries the next available assignment

---

## Smart Substitution

When a faculty member's leave is approved, the system automatically:
1. Identifies all affected timetable slots during the leave period
2. Queries available faculty with matching subject expertise
3. Ranks candidates by current weekly workload (lowest first)
4. Assigns the best-fit substitute for each slot
5. Saves the substitution timetable as a draft for admin review

---

## Database Schema

The relational model handles M:M:M relationships between Faculty, Subjects, and Departments:

- `faculty_subjects` — which subjects a faculty member is qualified to teach
- `faculty_departments` — which subject a faculty member teaches to a specific department
- `subject_departments` — which subjects are assigned to which departments
- `timetable_slots` — each row is one period: department + day + slot index → subject + faculty + room

---

## License

This project was developed as a Research and Review Project (RRP) for the Department of Computer Science and Design at Teegala Krishna Reddy Engineering College.
