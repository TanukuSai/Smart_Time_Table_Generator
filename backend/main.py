from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import database
from routers import auth, faculty, rooms, timetable, leaves, departments, subjects, constraints
import uvicorn
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.init_db()
    yield
    await database.close_db()

app = FastAPI(title="STTG API", version="2.0.0", lifespan=lifespan)

# CORS: allow all origins for deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(faculty.router, prefix="/api/faculty", tags=["faculty"])
app.include_router(rooms.router, prefix="/api/rooms", tags=["rooms"])
app.include_router(timetable.router, prefix="/api/timetable", tags=["timetable"])
app.include_router(leaves.router, prefix="/api/leaves", tags=["leaves"])
app.include_router(departments.router, prefix="/api/departments", tags=["departments"])
app.include_router(subjects.router, prefix="/api/subjects", tags=["subjects"])
app.include_router(constraints.router, prefix="/api/constraints", tags=["constraints"])

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "STTG API", "database": "supabase"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

