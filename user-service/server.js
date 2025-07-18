const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const path = require("path");

const app = express();

// Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static HTML, CSS, JS files from public/
app.use(express.static(path.join(__dirname, "public")));

const users = []; // In-memory DB: {id, username, passwordHash}

// Redirect base URL to index.html
app.get("/", (req, res) => {
  res.redirect("/index.html");
});

// Get all users (without passwords)
app.get("/users", (req, res) => {
  res.json(users.map(({ id, username }) => ({ id, username })));
});

// Register new user
app.post("/register", async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password)
    return res.status(400).json({ error: "Username and password required" });

  if (users.find(u => u.username === username))
    return res.status(400).json({ error: "Username already exists" });

  const hashedPassword = await bcrypt.hash(password, 10);
  users.push({ id: users.length + 1, username, password: hashedPassword });

  res.status(201).json({ message: "User registered successfully" });
});

// Login user, return JWT token
app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username);

  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  const validPass = await bcrypt.compare(password, user.password);
  if (!validPass) return res.status(401).json({ error: "Invalid credentials" });

  const token = jwt.sign({ userId: user.id }, "secretkey", { expiresIn: '1h' });
  res.json({ token });
});

// Start server
const PORT = 3001;
app.listen(PORT, () => console.log(`User Service running on port ${PORT}`));