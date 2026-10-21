from fastapi import FastAPI, APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv
import secrets


load_dotenv()

app = FastAPI()

router = APIRouter(prefix="/users")


# Database
async def get_db():
    return await asyncpg.connect(
        os.getenv("DATABASE_URL")
    )


# Request model
class CreateUser(BaseModel):
    name: str
    email: str
    age: int | None = None

class AdminLogin(BaseModel):
    username: str
    password: str


# ---------------------------------------------
# Super Admin Dependency (protects routes)
# ---------------------------------------------

async def require_super_admin(authorization:str|None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Expected: Bearer <token>"
        )

    token = authorization.split(" ")[1]

    db = await get_db()
    admin = await db.fetchrow(
        "select id, username, email from super_admin where token = $1",
        token
    )
    await db.close()

    if not admin:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only Super admins can perform this action"
        )

    return admin


# ---------------------------------------------
# Super Admin Login Route
# ---------------------------------------------


@app.post("/admin/route")
async def admin_login(creds:AdminLogin):
    db = await get_db()
    admin =await db.fetchrow(
        "select id,username from super_admin where username = $1 and password = $2",
        creds.username,
        creds.password
    )

    if not admin:
        await db.close()
        raise HTTPException(status_code=401,
        detail="Invalid username or password")

    # Generate a secure token and store it
    new_token=secrets.token_hex(32)
    await db.execute(
        "update super_admin set token = $1 where id = $2",
        new_token,
        admin["id"]
    )
    await db.close()

    return {
        "message": "Login successful",
        "token": new_token,
        "token_type": "bearer"
    }
    

# ---------------------------------------------
# Protected User Creation (Only Super Admin)
# ---------------------------------------------


@router.post("/", status_code=201)
async def create_user(
    user:CreateUser,
    admin = Depends(require_super_admin)  # <--- Enforces super admin check
):

    db = await get_db()
    result = await db.fetchrow(
        """
        INSERT INTO users(name, email, age)
        VALUES($1, $2, $3)
        RETURNING *
        """,
        user.name,
        user.email,
        user.age
    )

    await db.close()
    return result

# Authentication dependency
async def authenticate():
    # normally inspect Authorization header
    return {
        "id": 123,
        "name": "Salman"
    }
# router = APIRouter(prefix="/users", dependencies=[Depends(authenticate)])

# GET /users
@router.get("/")
async def get_users(
    page: int = 1,
    limit: int = 10
):

    offset = (page - 1) * limit

    db = await get_db()

    users = await db.fetch(
        """
        SELECT id, name, email
        FROM users
        LIMIT $1 OFFSET $2
        """,
        limit,
        offset
    )

    await db.close()

    return {
        "page": page,
        "limit": limit,
        "users": users
    }


# GET /users/:id
@router.get("/{id}")
async def get_user(id: int):

    db = await get_db()

    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        id
    )

    await db.close()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

# Protected route
@app.get("/profile")
async def profile(
    current_user = Depends(authenticate)
):

    db = await get_db()

    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        current_user["id"]
    )

    await db.close()

    return user


app.include_router(router)