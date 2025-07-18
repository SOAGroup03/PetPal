const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

const users = []; // in-memory DB: { id, username, password(hashed) }

// Register new user
const registerUser = async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: "Username and password required" });
  }
  if (users.find(u => u.username === username)) {
    return res.status(400).json({ error: "Username already exists" });
  }
  const hashed = await bcrypt.hash(password, 10);
  users.push({ id: users.length + 1, username, password: hashed });
  res.status(201).json({ message: "User registered" });
};

// Login user and return JWT
const loginUser = async (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username);
  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  const validPass = await bcrypt.compare(password, user.password);
  if (!validPass) return res.status(401).json({ error: "Invalid credentials" });

  const token = jwt.sign({ userId: user.id }, "secretkey");
  res.json({ token });
};

// Get all users (no passwords returned)
const getUsers = (req, res) => {
  res.json(users.map(({ id, username }) => ({ id, username })));
};

// Add user for UI (username only, no password)
const addUser = (req, res) => {
  const { username } = req.body;
  if (!username) return res.status(400).json({ error: "Username required" });
  if (users.find(u => u.username === username))
    return res.status(400).json({ error: "Username already exists" });

  users.push({ id: users.length + 1, username, password: "" });
  res.status(201).json({ id: users.length, username });
};

module.exports = {
  registerUser,
  loginUser,
  getUsers,
  addUser
};