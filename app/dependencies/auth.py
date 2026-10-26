from fastapi import Depends, Header, HTTPException

from app.core.database import get_db


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
        "SELECT id, username, email FROM super_admin WHERE token = $1", token
    )
    if not admin:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Only Super admins can perform this action",
        )
    return admin


async def authenticate():
    return {"id": 123, "name": "Salman"}
