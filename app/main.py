from fastapi import FastAPI
from app.core.database import lifespan
from app.routers import users, admin

app = FastAPI(title="Backend Learning API", version="1.0.0", lifespan=lifespan)

# Register routers
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {"message": "Server is up and running!"}
