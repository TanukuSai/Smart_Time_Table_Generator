import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()

async def reset():
    conn = await asyncpg.connect(os.environ["SUPABASE_DB_URL"], ssl="require")
    
    # Drop all existing public tables in dependency order
    tables = [
        "substitutions",
        "timetable_history",
        "timetable_entries", "substitutions", "timeslots", "timetables",
        "faculty_subjects", "faculty_departments", "faculty",
        "subject_departments",
        "sections", "departments",
        "leave_requests", "timetable_slots", "constraints",
        "rooms", "subjects", "departments", "users"
    ]
    
    for t in tables:
        try:
            await conn.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
            print(f"Dropped: {t}")
        except Exception as e:
            print(f"Skip {t}: {e}")
    
    print("\nAll old tables dropped. Ready for fresh schema creation.")
    await conn.close()

asyncio.run(reset())
