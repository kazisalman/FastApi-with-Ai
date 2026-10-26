from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.dependencies.auth import require_super_admin
from app.schemas.user import CreateUser, UpdateUser

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
async def get_users(page: int = 1, limit: int = 10, db=Depends(get_db)):
    offset = (page - 1) * limit
    users = await db.fetch(
        "SELECT id, name, email FROM users LIMIT $1 OFFSET $2", limit, offset
    )
    return {"page": page, "limit": limit, "users": users}


@router.get("/{id}")
async def get_user(id: int, db=Depends(get_db)):
    user = await db.fetchrow("SELECT * FROM users WHERE id = $1", id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: CreateUser, admin=Depends(require_super_admin), db=Depends(get_db)
):
    return await db.fetchrow(
        "INSERT INTO users(name, email, age) VALUES($1, $2, $3) RETURNING *",
        user.name,
        user.email,
        user.age,
    )


@router.patch("/{id}")
async def update_user(id: int, user_data: UpdateUser, db=Depends(get_db)):
    updates = user_data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    set_clauses = [f"{k} = ${i}" for i, k in enumerate(updates.keys(), 1)]
    values = list(updates.values())
    values.append(id)

    query = f"""
        UPDATE users
        SET {", ".join(set_clauses)}
        WHERE id = ${len(values)}
        RETURNING *
    """
    updated_user = await db.fetchrow(query, *values)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db=Depends(get_db)):
    res = await db.execute("DELETE FROM users WHERE id = $1", id)
    if int(res.split(" ")[1]) == 0:
        raise HTTPException(status_code=404, detail="User not found")
