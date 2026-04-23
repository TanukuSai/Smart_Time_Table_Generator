import asyncio, asyncpg, os
from dotenv import load_dotenv
load_dotenv()

async def check():
    conn = await asyncpg.connect(os.environ["SUPABASE_DB_URL"], ssl="require")
    rows = await conn.fetch("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' ORDER BY table_name
    """)
    print("=== Existing tables ===")
    for r in rows:
        print(f"  {r['table_name']}")
    
    # Check column types that cause conflicts
    for tbl in ["users", "faculty", "subjects", "departments", "rooms"]:
        try:
            cols = await conn.fetch("""
                SELECT column_name, data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_schema='public' AND table_name=$1
                ORDER BY ordinal_position
            """, tbl)
            if cols:
                print(f"\n--- {tbl} columns ---")
                for c in cols:
                    print(f"  {c['column_name']}: {c['data_type']} ({c['udt_name']})")
        except:
            pass
    
    await conn.close()

asyncio.run(check())
