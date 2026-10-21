# Node.js (Express) vs. Python (FastAPI) Side-by-Side

Two comprehensive, production-pattern, single-file servers performing the exact same tasks.

## Files
- [`express_server.js`](./express_server.js): Express, `pg` PostgreSQL pool, Zod validation, JWT auth, custom middleware, CRUD routes.
- [`fastapi_server.py`](./fastapi_server.py): FastAPI, `asyncpg` pool, Pydantic DTOs, Dependency Injection auth, `@app.middleware`, CRUD routes.

---

## How to Run

### 1. Running the Express Server
```bash
npm init -y
npm install express pg jsonwebtoken bcryptjs zod cors dotenv
node express_server.js
```
Runs on `http://localhost:3000`.

### 2. Running the FastAPI Server
```bash
# Create & activate a virtual environment (Python's equivalent to node_modules isolation)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install fastapi "uvicorn[standard]" asyncpg pyjwt "passlib[bcrypt]" "pydantic[email]"

# Start server with live reload
python fastapi_server.py
```
Runs on `http://localhost:3000`.
- Interactive Swagger UI: `http://localhost:3000/docs`
- ReDoc UI: `http://localhost:3000/redoc`

---

## Section-by-Section Comparison Guide

| Section | Express (`express_server.js`) | FastAPI (`fastapi_server.py`) |
| :--- | :--- | :--- |
| **1. Config** | `process.env.VAR \|\| fallback` | `os.getenv("VAR", fallback)` |
| **2. Database** | `new Pool(...)` | `asyncpg.create_pool(...)` inside `lifespan` |
| **3. Middleware** | `app.use((req, res, next) => { ... next() })` | `@app.middleware("http") async def mw(req, call_next)` |
| **4. Validation** | `z.object({ email: z.string().email() })` | `class UserDTO(BaseModel): email: EmailStr` |
| **5. Auth Guard** | `requireAuth` mutates `req.user = decoded; next()` | `CurrentUser = Annotated[Token, Depends(get_current_user)]` |
| **6. Query Params** | `PostQuerySchema.parse(req.query)` | `page: int = Query(default=1, ge=1)` |
| **7. Route Params** | `/posts/:id` + `parseInt(req.params.id)` | `/posts/{post_id}` + `post_id: int = Path(...)` |
| **8. Body Parser** | `CreatePostSchema.parse(req.body)` | `post_in: CreatePostDTO` (automatic) |
| **9. Error Handler** | `app.use((err, req, res, next) => { ... })` | `@app.exception_handler(Exception)` |
# fastApi-with-Ai-LLMs
