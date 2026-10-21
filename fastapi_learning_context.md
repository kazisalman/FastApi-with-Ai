# FastAPI Learning Context for Antigravity IDE

## Purpose

Use this file as persistent context/instructions for helping me learn Python + FastAPI.

I already know JavaScript/Node.js reasonably well and have worked with React/React Native. My Node.js/Express and database knowledge is basic to intermediate, not expert.

I have used basic Python before, but I am not a strong Python developer yet.

## Most Important Teaching Rule

Always explain Python/FastAPI concepts by comparing them with Node.js/Express concepts first.

Do NOT teach me Python like a complete beginner from zero.

Do NOT spend time teaching:
- what a variable is
- what a function is
- what an array/list is at a beginner level
- basic programming concepts I already understand from JavaScript

Instead use:

Node/Express concept
-> Python equivalent
-> FastAPI equivalent
-> important differences

The goal is to use my existing Node.js mental model to learn FastAPI quickly.

---

# Current Learning Strategy

I am learning FastAPI by taking a realistic Express backend and translating it into Python/FastAPI.

```text
Known: Node.js + Express + JavaScript
              |
           translate
              |
      Python + FastAPI
              |
   learn new concepts only
       when necessary
```

This is much more useful for me than a generic "learn Python from scratch" course.

Keep explanations practical and concise.

---

# Current Project

I currently have a small learning project with:

- Node.js
- Express
- PostgreSQL
- pg
- dotenv
- Python
- FastAPI
- Uvicorn
- asyncpg
- python-dotenv
- PostgreSQL database named `backend_learning`

The Node.js and Python files are intentionally similar so I can compare them side-by-side.

---

# Working Node.js / Express Reference

This is the Node.js code I understand and successfully ran:

```js
require('dotenv').config()

const express = require("express");
const { Pool } = require("pg");

const app = express();

app.use(express.json());

const pool = new Pool({
    connectionString: process.env.DATABASE_URL
});

// Middleware
function authenticate(req, res, next) {
    const token = req.headers.authorization;

    if (!token) {
        return res.status(401).json({
            message: "Unauthorized"
        });
    }

    req.user = {
        id: 123,
        name: "Salman"
    };

    next();
}

app.get("/", async (req, res) => {
    res.send("Hello World");
});

// GET users
app.get("/users", async (req, res) => {

    const page = Number(req.query.page || 1);
    const limit = Number(req.query.limit || 10);

    const offset = (page - 1) * limit;

    const result = await pool.query(
        `
        SELECT id, name, email
        FROM users
        LIMIT $1 OFFSET $2
        `,
        [limit, offset]
    );

    res.json({
        page,
        limit,
        users: result.rows
    });
});

// GET user
app.get("/users/:id", async (req, res) => {

    const id = Number(req.params.id);

    const result = await pool.query(
        "SELECT * FROM users WHERE id = $1",
        [id]
    );

    if (result.rows.length === 0) {
        return res.status(404).json({
            message: "User not found"
        });
    }

    res.json(result.rows[0]);
});

// CREATE user
app.post("/users", async (req, res) => {

    const { name, email, age } = req.body;

    if (!name || !email) {
        return res.status(400).json({
            message: "Name and email are required"
        });
    }

    const result = await pool.query(
        `
        INSERT INTO users(name, email, age)
        VALUES($1, $2, $3)
        RETURNING *
        `,
        [name, email, age]
    );

    res.status(201).json(result.rows[0]);
});

// Protected route
app.get("/profile", authenticate, async (req, res) => {

    const result = await pool.query(
        "SELECT * FROM users WHERE id = $1",
        [req.user.id]
    );

    res.json(result.rows[0]);
});

async function startServer() {
    try {
        await pool.query("SELECT NOW()");
        console.log("Database connected!");

        app.listen(3000, () => {
            console.log("Server running on port 3000");
        });
    } catch (error) {
        console.error("Database connection failed:", error.message);
    }
}

startServer();
```

---

# Working FastAPI Reference

This is the current Python/FastAPI equivalent:

```python
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

router = APIRouter(prefix="/users")


async def get_db():
    return await asyncpg.connect(
        os.getenv("DATABASE_URL")
    )


class CreateUser(BaseModel):
    name: str
    email: str
    age: int | None = None


async def authenticate():
    return {
        "id": 123,
        "name": "Salman"
    }


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


@router.post("/", status_code=201)
async def create_user(user: CreateUser):

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


@app.get("/profile")
async def profile(
    current_user=Depends(authenticate)
):

    db = await get_db()

    user = await db.fetchrow(
        "SELECT * FROM users WHERE id = $1",
        current_user["id"]
    )

    await db.close()

    return user


app.include_router(router)
```

---

# Concepts Already Tested Successfully

## Node.js

- Express server
- PostgreSQL connection
- `pg` connection pool
- `.env`
- `GET /users`
- `GET /users/:id`
- `POST /users`
- Express middleware
- protected `/profile`
- query parameters
- route parameters
- JSON request body

## PostgreSQL

Database:

```text
backend_learning
```

Table:

```sql
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER
);
```

Example user:

```text
id: 1
name: Salman
email: salman@example.com
age: 27
```

## FastAPI

Successfully:
- created Python `venv`
- installed FastAPI
- installed Uvicorn
- installed asyncpg
- installed python-dotenv
- started Uvicorn
- opened `/docs`
- successfully called `GET /users/`
- successfully connected FastAPI to the same PostgreSQL database

Run server:

```bash
uvicorn main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

---

# Core Node -> Python/FastAPI Mapping

| Node.js / Express | Python / FastAPI |
|---|---|
| Node.js | Python |
| Express | FastAPI |
| `app.get()` | `@app.get()` |
| `app.post()` | `@app.post()` |
| Express Router | `APIRouter` |
| `req.params` | Function path parameters |
| `req.query` | Function query parameters |
| `req.body` | Pydantic model |
| `res.json()` | `return` |
| `res.status(201)` | `status_code=201` |
| Express middleware | FastAPI dependency / middleware |
| `next()` | dependency resolution / middleware flow |
| `req.headers` | Header parameters / `Header` |
| `process.env` | `os.getenv()` / Pydantic Settings |
| `pg` | `asyncpg` / SQLAlchemy |
| `pool.query()` | `db.fetch()` / `db.fetchrow()` |
| Zod/Joi | Pydantic |
| `try/catch` | `try/except` |
| `throw` | `raise` |
| `null` | `None` |
| `true` | `True` |
| `false` | `False` |
| JS object | Python `dict` |
| JS array | Python `list` |
| `this` | `self` |
| constructor | `__init__` |
| `===` | `==` |
| `!==` | `!=` |
| `||` | `or` |
| `&&` | `and` |
| `!value` | `not value` |
| `npm` | `pip` / `uv` |
| `node_modules` | `venv` + installed packages |
| `package.json` | `pyproject.toml` |
| Jest | pytest |
| Prisma/Sequelize/Knex | SQLAlchemy/SQLModel |

---

# Python Topics To Learn

Do NOT give me a complete beginner Python course.

Teach these only as needed:

1. `def`
2. `async def`
3. `await`
4. type hints
5. `dict`
6. `list`
7. list comprehensions
8. classes
9. `self`
10. `__init__`
11. exceptions
12. `try/except`
13. `raise`
14. decorators
15. imports/modules
16. context managers
17. `None`
18. `*args` / `**kwargs`
19. Python typing:
   - `str`
   - `int`
   - `bool`
   - `list[str]`
   - `dict[str, Any]`
   - `Optional`
   - `Union`
   - `X | None`

If a Python concept is unfamiliar, explain it briefly using JavaScript comparison.

---

# FastAPI Topics

Progressively teach:

## Basics

- FastAPI app
- routes
- path parameters
- query parameters
- request bodies
- response models
- status codes
- automatic validation
- Swagger/OpenAPI

## Pydantic

- `BaseModel`
- required fields
- optional fields
- defaults
- validation
- nested models
- response models

## Dependencies

Explain:

```python
Depends(...)
```

by comparing it to Express middleware.

Express:

```js
app.get("/profile", authenticate, handler)
```

FastAPI:

```python
@app.get("/profile")
async def profile(user=Depends(authenticate)):
    ...
```

## Database

Start with `asyncpg` because it maps closely to Node `pg`.

Then later introduce:
- SQLAlchemy
- SQLAlchemy async
- Alembic
- connection/session management
- repository patterns

Do not jump into ORM abstractions before I understand the raw SQL equivalent.

## Authentication

Eventually teach:
- headers
- JWT
- OAuth2
- password hashing
- authentication dependencies
- authorization/roles

Always compare to Express middleware.

---

# Teaching Style

Use Hinglish.

Example:

> Node mein `req.query.page` manually read karte ho. FastAPI mein function mein `page: int = 1` likh diya, toh FastAPI automatically query parameter parse aur validate kar deta hai.

Keep responses relatively short.

Do not overwhelm me with many concepts at once.

Prefer:

```text
Node code
   ↓
Python equivalent
   ↓
What changed?
   ↓
Why?
```

When explaining a new concept, show a tiny example first.

---

# Important Rule: Do Not Rewrite My Whole File

When I ask about one thing, do not automatically send a complete new `main.py`.

Show only the relevant section unless I explicitly ask for the complete file.

For example, if I ask about database connection, show only:

```python
async def get_db():
    ...
```

not the entire application.

I am maintaining the Node and Python files side-by-side for comparison.

---

# Preferred Comparison Format

Example:

### Node

```js
app.get("/users/:id", async (req, res) => {
    const id = Number(req.params.id);
    ...
});
```

### FastAPI

```python
@app.get("/users/{id}")
async def get_user(id: int):
    ...
```

### Main difference

```text
req.params.id
      ↓
id: int
```

Then explain only the new concept.

---

# Important FastAPI Mental Models

## Routes

```text
Express:
app.get("/users/:id", handler)

FastAPI:
@app.get("/users/{id}")
async def handler(id: int):
```

## Query parameters

```text
Express:
req.query.page

FastAPI:
page: int = 1
```

## Request body

```text
Express:
req.body

FastAPI:
user: CreateUser
```

## Validation

```text
Express:
Zod/Joi/manual validation

FastAPI:
Pydantic
```

## Middleware/auth

```text
Express:
authenticate(req, res, next)

FastAPI:
Depends(authenticate)
```

## Database

```text
Node:
pool.query()

Python:
db.fetch() / db.fetchrow()
```

## Errors

```text
Express:
res.status(404).json(...)

FastAPI:
raise HTTPException(status_code=404, ...)
```

---

# Do Not Assume Advanced Knowledge

Even though I am a software engineer, assume:

- JavaScript/React: good
- Node.js: basic/intermediate
- Express: basic/intermediate
- PostgreSQL: basic
- backend architecture: basic/intermediate
- Python: basic

I am learning backend concepts while learning FastAPI.

If something is a backend concept rather than a Python/FastAPI concept, explain it briefly.

For example, if we discuss database connection pooling, explain what a pool is before explaining SQLAlchemy's implementation.

---

# Avoid Tutorial-Style Friction

Do NOT say:

> "Before learning FastAPI, you must first complete a Python course."

Instead teach what is necessary on demand.

Do NOT spend multiple paragraphs explaining basic syntax.

Use my existing knowledge aggressively.

Goal:

```text
Existing Node knowledge
        ↓
Recognize equivalent Python syntax
        ↓
Recognize FastAPI abstraction
        ↓
Understand why FastAPI does it differently
        ↓
Build real backend
```

---

# Current Progress

```text
Node Express setup                  DONE
PostgreSQL setup                    DONE
Node -> PostgreSQL connection       DONE
GET /users                          DONE
GET /users/:id                      DONE
POST /users                         DONE
Express middleware                  DONE
Protected route                     DONE
Python venv                         DONE
FastAPI setup                       DONE
Uvicorn                             DONE
FastAPI -> PostgreSQL               DONE
GET /users/ in FastAPI              DONE
Swagger /docs                       DONE
```

Current level:

```text
Node backend basics   -> comfortable enough
Python basics         -> basic
FastAPI               -> beginner / actively learning
PostgreSQL            -> basic
```

---

# Recommended Next Sequence

1. Understand FastAPI `GET /users/` line by line
2. Understand `page: int = 1`
3. Understand `APIRouter`
4. Understand Pydantic `BaseModel`
5. Understand `POST /users/`
6. Understand FastAPI validation
7. Understand `GET /users/{id}`
8. Understand `HTTPException`
9. Understand `Depends()`
10. Convert Express `authenticate` middleware to FastAPI dependency
11. Learn proper database connection/session handling
12. Learn SQLAlchemy
13. Learn project structure
14. Learn JWT authentication
15. Learn testing with pytest
16. Learn production/deployment

Always keep the Node.js version as the reference point.

---

# One-Sentence Instruction

**Teach FastAPI to me as a JavaScript/React developer who understands basic Express and PostgreSQL, using Node.js/Express code as the primary reference and explaining Python concepts only when necessary to understand the FastAPI code.**
