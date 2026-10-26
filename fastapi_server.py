from fastapi import Request, status
from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv
import secrets


load_dotenv()

app = FastAPI()

router = APIRouter(prefix="/users")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start
    app.state.pool = await asyncpg.create_pool(
        os.getenv("DATABASE_URL"),
        min_size=5,  # keep at least 5 connections ready
        max_size=20,  # expand up to 20 under loa
    )

    print(" Database connection pool created!")
    yield  # 🚀 The application runs and serves requests here

    # --- SHUTDOWN ---
    # Gracefully close all connections when the server stops
    await app.state.pool.close()
    print("🔌 Database connection pool closed!")


# Pass lifespan to FastAPI
app = FastAPI(lifespan=lifespan)


# # Database
# async def get_db():
#     return await asyncpg.connect(
#         os.getenv("DATABASE_URL")
#     )


# Database
async def get_db(request: Request):
    # Acquire a connection from the pool
    async with request.app.state.pool.acquire() as connection:
        yield connection  # Give connection to the route
        # When route finishes or throws, the connection automatically goes back to the pool!


# Request model
class CreateUser(BaseModel):
    name: str
    email: str
    age: int | None = None


class UpdateUser(BaseModel):
    name: str | None = None
    email: str | None = None
    age: int | None = None


class AdminLogin(BaseModel):
    username: str
    password: str


# ---------------------------------------------
# Super Admin Dependency (protects routes)
# ---------------------------------------------


async def require_super_admin(
    authorization: str | None = Header(None), db=Depends(get_db)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header. Expected: Bearer <token>",
        )

    token = authorization.split(" ")[1]
    admin = await db.fetchrow(
        "select id, username, email from super_admin where token = $1", token
    )
    if not admin:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only Super admins can perform this action",
        )

    return admin


# ---------------------------------------------
# Super Admin Login Route
# ---------------------------------------------


@app.post("/admin/route")
async def admin_login(creds: AdminLogin, db=Depends(get_db)):
    admin = await db.fetchrow(
        "select id,username from super_admin where username = $1 and password = $2",
        creds.username,
        creds.password,
    )

    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate a secure token and store it
    new_token = secrets.token_hex(32)
    await db.execute(
        "update super_admin set token = $1 where id = $2", new_token, admin["id"]
    )

    return {"message": "Login successful", "token": new_token, "token_type": "bearer"}


# ---------------------------------------------
# Protected User Creation (Only Super Admin)
# ---------------------------------------------


@router.post("/", status_code=201)
async def create_user(
    user: CreateUser,
    admin=Depends(require_super_admin),  # <--- Enforces super admin check
    db=Depends(get_db),
):

    result = await db.fetchrow(
        """
        INSERT INTO users(name, email, age)
        VALUES($1, $2, $3)
        RETURNING *
        """,
        user.name,
        user.email,
        user.age,
    )

    return result


@router.patch("/{id}", status_code=201)
async def update_user(id: int, user_data: UpdateUser, db=Depends(get_db)):

    # 1. Extract only the fields provided by the caller
    updates = user_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=400, detail="No feilds provided to update")

    # 2. Build dynamic SET clause (e.g. "name = $1, age = $2")
    set_clauses = []
    # example ["Alice"]
    values = []

    for i, (key, value) in enumerate(updates.item(), start=1):
        set_clauses.append(f"{key} = ${i}")
        values.append(value)

    # The ID placeholder will be the next number: e.g. $3
    id_param_index = len(values) + 1
    values.append(id)

    query = f"""
        update users
        set {", ".join(set_clauses)}
        where id = ${id_param_index}
        returning *
    """

    # 3. Execute and fetch the updated row
    updated_user = await db.fetchrow(query, *values)

    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db=Depends(get_db)):

    result = await db.execute("delete from users where id = $1", id)

    # result looks like: "DELETE 1" or "DELETE 0"
    rows_deleted = int(result.split(" ")[1])

    if rows_deleted == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # With 204 No Content, we return nothing
    return None


# Authentication dependency
async def authenticate():
    # normally inspect Authorization header
    return {"id": 123, "name": "Salman"}


# GET /users
@router.get("/")
async def get_users(
    page: int = 1,
    limit: int = 10,
    db=Depends(get_db),  # <--- Injected directly by FastAPI
):

    offset = (page - 1) * limit
    # No need to manually open or close the connection!
    users = await db.fetch(
        """
        SELECT id, name, email
        FROM users
        LIMIT $1 OFFSET $2
        """,
        limit,
        offset,
    )
    return {"page": page, "limit": limit, "users": users}


# GET /users/:id
@router.get("/{id}")
async def get_user(id: int, db=Depends(get_db)):

    user = await db.fetchrow("SELECT * FROM users WHERE id = $1", id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# @router.patch("/{id}")
# async def update_user(id:int):


# Protected route
@app.get("/profile")
async def profile(current_user=Depends(authenticate), db=Depends(get_db)):

    user = await db.fetchrow("SELECT * FROM users WHERE id = $1", current_user["id"])

    return user


app.include_router(router)
