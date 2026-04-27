import base64
import zlib
import urllib.request
import os

mermaid_code = """classDiagram
    direction TB
    
    classDef admin fill:#d5e8d4,stroke:#82b366,stroke-width:2px,color:#000
    classDef user fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px,color:#000
    classDef faculty fill:#d5e8d4,stroke:#82b366,stroke-width:2px,color:#000
    classDef core fill:#fff2cc,stroke:#d6b656,stroke-width:2px,color:#000
    classDef action fill:#f8cecc,stroke:#b85450,stroke-width:2px,color:#000
    classDef timetable fill:#e1d5e7,stroke:#9673a6,stroke-width:2px,color:#000
    classDef meta fill:#f5f5f5,stroke:#666666,stroke-width:2px,color:#000

    class Admin {
        <<role>> Admin
        +manageDepartments()
        +manageFaculty()
        +manageRooms()
        +setupDepartments()
        +viewTimetable()
        +publishTimetable()
    }
    
    class User {
        +id: Serial PK
        +name: Text UNIQUE
        +password_hash: Text
        +role: Enum(admin/faculty/student)
        +admin_id: Integer FK
        +department_id: Integer FK
        +created_at: Timestamp
        +viewTimetable()
    }
    
    class Student {
        <<role>> Student
        +id: Serial PK
        +admin_id: Integer FK
        +name: Text
        +department_id: Integer FK
        +viewTimetable()
    }
    
    class Faculty {
        +id: Serial PK
        +user_id: Integer FK UNIQUE
        +employee_code: Text
        +max_weekly_hours: Integer
        +is_present: Integer
        +admin_id: Integer FK
        +submitLeaveRequest()
    }
    
    class Department {
        +id: Serial PK
        +name: Text
        +type: Enum(UG/PG)
        +semester: Integer
        +section: Text
        +strength: Integer
        +admin_id: Integer FK
        +room_id: Integer FK
        +lab_id: Integer FK
    }
    
    class Subject {
        +id: Serial PK
        +code: Text
        +name: Text
        +semester: Integer
        +classes_per_week: Integer
        +type: Enum(theory/lab)
        +admin_id: Integer FK
    }
    
    class Room {
        +id: Serial PK
        +room_id: Text
        +type: Enum(classroom/lab/hall)
        +capacity: Integer
        +is_available: Integer
        +admin_id: Integer FK
    }
    
    class TimetableHistory {
        +id: Serial PK
        +admin_id: Integer FK
        +name: Text
        +department_ids: JSONB
        +snapshot: JSONB
        +log: Text
        +status: Enum(draft/published)
        +type: Text
        +viewTimetable()
    }
    
    class TimetableSlot {
        +id: Serial PK
        +generation_id: Integer FK
        +day: Enum(Mon-Sun)
        +slot_index: Integer
        +slot_time: Text
        +subject_id: Integer FK
        +faculty_id: Integer FK
        +room_id: Integer FK
        +is_break: Integer
        +admin_id: Integer FK
    }
    
    class LeaveRequest {
        +id: Serial PK
        +admin_id: Integer FK
        +leave_type: Text(casual/medical)
        +status: Enum(pending/approved/denied)
        +admin_note: Text
        +start_date: Timestamp
        +end_date: Timestamp
        +approved_at: Timestamp
    }
    
    class Substitution {
        +id: Serial PK
        +leave_request_id: Integer FK
        +timetable_slot_id: Integer FK
        +original_faculty_id: Integer FK
        +substitute_faculty_id: Integer FK
        +day: Text
        +slot_index: Integer
        +subject_id: Integer FK
        +status: Text
        +created_at: Timestamp
        +admin_id: Integer FK
    }
    
    class Constraint {
        +id: Serial PK
        +is_builtin: Integer
        +config: JSONB
        +strength: Integer
        +is_enabled: Integer
        +category: Text
        +type: Enum(hard/soft)
        +admin_id: Integer FK
        +created_at: Timestamp
    }
    
    class faculty_subjects {
        <<junction>>
        +faculty_id: Integer FK
        +subject_id: Integer FK
    }
    
    class faculty_departments {
        <<junction>>
        +faculty_id: Integer FK
        +department_id: Integer FK
    }
    
    class subject_departments {
        <<junction>>
        +subject_id: Integer FK
        +department_id: Integer FK
    }

    %% Relationships
    User <|-- Admin
    User <|-- Student
    User <|-- Faculty
    
    Admin "1" --> "*" Faculty : managed
    Admin "1" --> "*" Department : managed
    Admin "1" --> "*" Room : managed
    
    Faculty "1" --> "*" LeaveRequest : triggers
    Faculty "1" --> "*" Substitution : substitutes
    
    Department "*" --> "1" Room : base_classroom
    Department "*" --> "1" Room : base_lab
    
    Subject "*" --> "1" Department : belongs_to
    Subject "*" --> "*" Room : uses
    
    TimetableHistory "1" --> "*" TimetableSlot : contains
    TimetableSlot "*" --> "1" Subject : assigns
    TimetableSlot "*" --> "1" Faculty : assigns
    TimetableSlot "*" --> "1" Room : allocates
    
    LeaveRequest "1" --> "*" Substitution : requires
    Substitution "*" --> "1" TimetableSlot : modifies
    
    %% Junction connections
    Faculty "1" --> "*" faculty_subjects
    Subject "1" --> "*" faculty_subjects
    
    Faculty "1" --> "*" faculty_departments
    Department "1" --> "*" faculty_departments
    
    Subject "1" --> "*" subject_departments
    Department "1" --> "*" subject_departments

    %% Apply Classes
    class Admin admin
    class Faculty faculty
    class User user
    class Student user
    class Department core
    class Subject core
    class Room core
    class TimetableHistory timetable
    class TimetableSlot timetable
    class LeaveRequest action
    class Substitution action
    class Constraint meta
    class faculty_subjects meta
    class faculty_departments meta
    class subject_departments meta
"""

compressed = zlib.compress(mermaid_code.encode('utf-8'), 9)
payload = base64.urlsafe_b64encode(compressed).decode('ascii')
url = f"https://kroki.io/mermaid/svg/{payload}"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response, open('UML_Class_Diagram.svg', 'wb') as out_file:
        out_file.write(response.read())
    print("Saved UML_Class_Diagram.svg")
except Exception as e:
    print("Failed to download SVG:", e)
