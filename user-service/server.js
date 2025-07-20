const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const path = require("path");
const app = express();

const JWT_SECRET = "secretkey"; // Ideally keep in env variables

// Middlewares
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from public folder
app.use(express.static(path.join(__dirname, "public")));

// Redirect root to home.html
app.get("/", (req, res) => {
  res.redirect("/home.html");
});

// In-memory users DB
const users = [];

// JWT auth middleware
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ error: "Missing token" });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ error: "Invalid token" });
    req.user = user;
    next();
  });
}

// API: Get all users (without passwords)
app.get("/users", (req, res) => {
  res.json(users.map(({ id, username }) => ({ id, username })));
});

// API: Register user with hashed password
app.post("/register", async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password)
    return res.status(400).json({ error: "Username and password required" });

  if (users.find(u => u.username === username))
    return res.status(400).json({ error: "Username already exists" });

  const hashed = await bcrypt.hash(password, 10);
  users.push({ id: users.length + 1, username, password: hashed });
  res.status(201).json({ message: "User registered" });
});

// API: Login user and return JWT token
app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username);
  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  const validPass = await bcrypt.compare(password, user.password);
  if (!validPass) return res.status(401).json({ error: "Invalid credentials" });

  const token = jwt.sign({ userId: user.id, username: user.username }, JWT_SECRET, { expiresIn: '1h' });
  res.json({ token });
});

// API: Verify token (optional)
app.get("/verify-token", (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ error: "Missing authorization header" });

  const token = authHeader.split(" ")[1];
  jwt.verify(token, JWT_SECRET, (err, decoded) => {
    if (err) return res.status(401).json({ error: "Invalid or expired token" });
    res.json({ valid: true, userId: decoded.userId, username: decoded.username });
  });
});

// API: Update profile (username only)
app.put("/update-profile", authenticateToken, (req, res) => {
  const { username } = req.body;
  const userId = req.user.userId;

  if (!username) {
    return res.status(400).json({ error: "Username is required" });
  }

  if (users.some(u => u.username === username && u.id !== userId)) {
    return res.status(400).json({ error: "Username already taken" });
  }

  const user = users.find(u => u.id === userId);
  if (!user) return res.status(404).json({ error: "User not found" });

  user.username = username;
  res.json({ message: "Profile updated" });
});

// NEW: API: Change password
app.put("/change-password", authenticateToken, async (req, res) => {
  const { oldPassword, newPassword } = req.body;
  const userId = req.user.userId;

  if (!oldPassword || !newPassword) {
    return res.status(400).json({ error: "Old password and new password are required" });
  }

  const user = users.find(u => u.id === userId);
  if (!user) return res.status(404).json({ error: "User not found" });

  const isOldPasswordValid = await bcrypt.compare(oldPassword, user.password);
  if (!isOldPasswordValid) {
    return res.status(401).json({ error: "Old password is incorrect" });
  }

  const hashedNewPassword = await bcrypt.hash(newPassword, 10);
  user.password = hashedNewPassword;

  res.json({ message: "Password changed successfully" });
});

// Start server
app.listen(3001, () => console.log("User Service running at 3001"));