import secrets
from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_db
from app.schemas.admin import AdminLogin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/login")
async def admin_login(creds: AdminLogin, db=Depends(get_db)):
    admin = await db.fetchrow(
        "SELECT id, username FROM super_admin WHERE username = $1 AND password = $2",
        creds.username,
        creds.password,
    )
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    new_token = secrets.token_hex(32)
    await db.execute(
        "UPDATE super_admin SET token = $1 WHERE id = $2", new_token, admin["id"]
    )
    return {"message": "Login successful", "token": new_token, "token_type": "bearer"}
