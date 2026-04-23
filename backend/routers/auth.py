from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from database import get_db
from auth_utils import verify_password, hash_password, create_token, decode_token

router = APIRouter()
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    institution: str = ""

@router.post("/login")
async def login(req: LoginRequest, db=Depends(get_db)):
    user = await db.fetchrow("SELECT * FROM users WHERE email = $1", req.email)
    if not user or not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Determine admin_id
    admin_id = user["admin_id"] if user["admin_id"] else user["id"]
    department_id = user.get("department_id")

    token = create_token(user["id"], user["role"], user["name"], admin_id=admin_id, department_id=department_id)
    return {
        "token": token,
        "role": user["role"],
        "name": user["name"],
        "id": user["id"],
        "admin_id": admin_id,
        "department_id": department_id,
        "institution": user.get("institution", ""),
    }

@router.post("/register")
async def register(req: RegisterRequest, db=Depends(get_db)):
    existing = await db.fetchrow("SELECT id FROM users WHERE email = $1", req.email)
    if existing:
        raise HTTPException(400, "Email already registered")

    import json
    async with db.transaction():
        user_id = await db.fetchval(
            "INSERT INTO users (name, email, password_hash, role, institution) VALUES ($1, $2, $3, $4, $5) RETURNING id",
            req.name, req.email, hash_password(req.password), "admin", req.institution
        )

        # Create built-in constraints for this admin
        for name, ctype, category in [
            ("No faculty double-booking", "hard", "no_faculty_double_booking"),
            ("No room double-booking", "hard", "no_room_double_booking"),
            ("Respect max weekly hours", "hard", "respect_max_weekly_hours"),
            ("Balance faculty workload", "soft", "balance_workload"),
        ]:
            await db.execute("""
                INSERT INTO constraints (name, type, category, is_enabled, is_builtin, config, admin_id)
                VALUES ($1, $2, $3, 1, 1, $4::jsonb, $5)
            """, name, ctype, category, json.dumps({}), user_id)

    token = create_token(user_id, "admin", req.name, admin_id=user_id)
    return {
        "token": token,
        "role": "admin",
        "name": req.name,
        "id": user_id,
        "admin_id": user_id,
        "institution": req.institution,
    }

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return decode_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

def get_admin_id(user: dict) -> int:
    """Extract admin_id from JWT payload. For admins, it's their own id."""
    aid = user.get("admin_id")
    if aid is not None:
        return int(aid)
    return int(user["sub"])

async def require_admin(user=Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def require_faculty(user=Depends(get_current_user)):
    if user["role"] not in ("admin", "faculty"):
        raise HTTPException(status_code=403, detail="Faculty access required")
    return user
