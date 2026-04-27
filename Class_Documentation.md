# STTG System - Class Documentation

This document provides a detailed breakdown of the entities (classes) within the Smart Time Table Generator (STTG), their attributes, and their associated behaviors/methods, matching the exact ER schema layout.

## 1. User
Represents a registered user in the system.
**Attributes:**
- `id` (Serial PK)
- `name` (Text UNIQUE)
- `password_hash` (Text)
- `role` (Enum: admin/faculty/student)
- `admin_id` (Integer FK)
- `department_id` (Integer FK)
- `created_at` (Timestamp)

**Methods:**
- `viewTimetable()`

---

## 2. Admin (Inherits User)
Represents a multi-tenant administrator managing their institution.
**Methods:**
- `manageDepartments()`
- `manageFaculty()`
- `manageRooms()`
- `setupDepartments()`
- `viewTimetable()`
- `publishTimetable()`

---

## 3. Student (Inherits User)
Represents a student.
**Attributes:**
- `id` (Serial PK)
- `admin_id` (Integer FK)
- `name` (Text)
- `department_id` (Integer FK)

**Methods:**
- `viewTimetable()`

---

## 4. Faculty
Represents a teacher or professor in the institution.
**Attributes:**
- `id` (Serial PK)
- `user_id` (Integer FK UNIQUE)
- `employee_code` (Text)
- `max_weekly_hours` (Integer)
- `is_present` (Integer)
- `admin_id` (Integer FK)

**Methods:**
- `submitLeaveRequest()`

---

## 5. Department
Represents a specific class/cohort of students.
**Attributes:**
- `id` (Serial PK)
- `name` (Text)
- `type` (Enum: UG/PG)
- `semester` (Integer)
- `section` (Text)
- `strength` (Integer)
- `admin_id` (Integer FK)
- `room_id` (Integer FK) - *Base Classroom for theory*
- `lab_id` (Integer FK) - *Base Lab for practicals*

---

## 6. Subject
Represents an academic course.
**Attributes:**
- `id` (Serial PK)
- `code` (Text)
- `name` (Text)
- `semester` (Integer)
- `classes_per_week` (Integer)
- `type` (Enum: theory/lab)
- `admin_id` (Integer FK)

---

## 7. Room
Represents a physical space.
**Attributes:**
- `id` (Serial PK)
- `room_id` (Text)
- `type` (Enum: classroom/lab/hall)
- `capacity` (Integer)
- `is_available` (Integer)
- `admin_id` (Integer FK)

---

## 8. TimetableHistory
Represents a generated timetable.
**Attributes:**
- `id` (Serial PK)
- `admin_id` (Integer FK)
- `name` (Text)
- `department_ids` (JSONB)
- `snapshot` (JSONB)
- `log` (Text)
- `status` (Enum: draft/published)
- `type` (Text)

**Methods:**
- `viewTimetable()`

---

## 9. TimetableSlot
Represents an individual 45-minute block assigned in the timetable.
**Attributes:**
- `id` (Serial PK)
- `generation_id` (Integer FK)
- `day` (Enum: Mon-Sun)
- `slot_index` (Integer)
- `slot_time` (Text)
- `subject_id` (Integer FK)
- `faculty_id` (Integer FK)
- `room_id` (Integer FK)
- `is_break` (Integer)
- `admin_id` (Integer FK)

---

## 10. LeaveRequest
Represents a request for faculty absence.
**Attributes:**
- `id` (Serial PK)
- `admin_id` (Integer FK)
- `leave_type` (Text: casual/medical)
- `status` (Enum: pending/approved/denied)
- `admin_note` (Text)
- `start_date` (Timestamp)
- `end_date` (Timestamp)
- `approved_at` (Timestamp)

---

## 11. Substitution
Represents a dynamic substitution mapping for an absent faculty member.
**Attributes:**
- `id` (Serial PK)
- `leave_request_id` (Integer FK)
- `timetable_slot_id` (Integer FK)
- `original_faculty_id` (Integer FK)
- `substitute_faculty_id` (Integer FK)
- `day` (Text)
- `slot_index` (Integer)
- `subject_id` (Integer FK)
- `status` (Text)
- `created_at` (Timestamp)
- `admin_id` (Integer FK)

---

## 12. Constraint
Represents configurable scheduling rules.
**Attributes:**
- `id` (Serial PK)
- `is_builtin` (Integer)
- `config` (JSONB)
- `strength` (Integer)
- `is_enabled` (Integer)
- `category` (Text)
- `type` (Enum: hard/soft)
- `admin_id` (Integer FK)
- `created_at` (Timestamp)

---

## 13. TimetableGenerator (Service)
Handles the Constraint Satisfaction Problem (CSP) logic for dynamic scheduling and enforcing custom constraints.
**Attributes:**
- `slots_per_day` (Integer)
- `working_days` (Integer)
- `start_time` (Text)
- `class_duration` (Integer)
- `break_duration` (Integer)

**Methods:**
- `generate_timetable(department_ids, opts)`
- `pre_schedule_labs()`
- `enforce_theory_constraints()`

---

## Junction Tables
These represent many-to-many relationships in the database schema:
- **`faculty_subjects`**: Links `faculty_id` to `subject_id`.
- **`faculty_departments`**: Links `faculty_id` to `department_id`.
- **`subject_departments`**: Links `subject_id` to `department_id`.
