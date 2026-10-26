import os
from contextlib import asynccontextmanager

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Request

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        os.getenv("DATABASE_URL"),
        min_size=5,
        max_size=20,
    )
    print("✅ Database connection pool created!")
    yield
    await app.state.pool.close()
    print("🔌 Database connection pool closed!")


async def get_db(request: Request):
    async with request.app.state.pool.acquire() as connection:
        yield connection
