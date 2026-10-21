require('dotenv').config()

const express = require("express");
const { Pool } = require("pg");

const app = express();

app.use(express.json());

const pool = new Pool({
    connectionString: process.env.DATABASE_URL
});
// const pool=new Pool({ host:"localhost", port: 5432, database:"mydb", user:"postgres", password:"12345678"})

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


// Protected route
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
    console.log("✅ Database connected!");

    app.listen(3000, () => {
      console.log("🚀 Server running on port 3000");
    });
  } catch (error) {
    console.error("❌ Database connection failed:", error.message);
  }
}

startServer();


// app.listen(3000, () => {
//     console.log("Server running");
// });