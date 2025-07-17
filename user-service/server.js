const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from the 'public' folder
app.use(express.static('public'));

const users = []; // In-memory DB with {id, username, password}

// Registration - POST /register expects { username, password }
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

// Login - POST /login expects { username, password }
app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  const user = users.find(u => u.username === username);
  if (!user) return res.status(401).json({ error: "Invalid credentials" });

  const validPass = await bcrypt.compare(password, user.password);
  if (!validPass) return res.status(401).json({ error: "Invalid credentials" });

  const token = jwt.sign({ userId: user.id }, "secretkey");
  res.json({ token });
});

// GET /users - Serve HTML UI if browser, else JSON API
app.get('/users', (req, res) => {
  const acceptsHtml = req.headers.accept && req.headers.accept.includes('text/html');
  if (acceptsHtml) {
    res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>PetPal Users</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
    </head>
    <body>
      <div class="container my-5">
        <h1 class="mb-4 text-primary">PetPal User Management</h1>

        <div class="mb-3">
          <label for="username" class="form-label">Add New User (username only)</label>
          <input type="text" class="form-control" id="username" placeholder="Enter username" />
          <button class="btn btn-success mt-2" onclick="addUser()">Add User</button>
        </div>

        <h2 class="mt-5 mb-3">Users List</h2>
        <button class="btn btn-primary mb-3" onclick="fetchUsers()">Refresh Users</button>
        <ul id="usersList" class="list-group"></ul>
      </div>

      <script>
        async function addUser() {
          const nameInput = document.getElementById('username');
          const username = nameInput.value.trim();
          if (!username) {
            alert('Please enter a username');
            return;
          }
          try {
            const res = await fetch('/users', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ username })
            });
            if (!res.ok) throw new Error('Failed to add user');
            const data = await res.json();
            alert('User added: ' + data.username + ' (ID: ' + data.id + ')');
            nameInput.value = '';
            fetchUsers();
          } catch (e) {
            alert(e.message);
          }
        }

        async function fetchUsers() {
          try {
            const res = await fetch('/users', {
              headers: { 'Accept': 'application/json' }
            });
            if (!res.ok) throw new Error('Failed to fetch users');
            const users = await res.json();
            const list = document.getElementById('usersList');
            list.innerHTML = '';
            if (users.length === 0) {
              list.innerHTML = '<li class="list-group-item">No users found.</li>';
            } else {
              users.forEach(user => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = user.id + ': ' + user.username;
                list.appendChild(li);
              });
            }
          } catch (e) {
            alert(e.message);
          }
        }

        fetchUsers();
      </script>

      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    `);
  } else {
    // Return JSON API
    // Return users but WITHOUT passwords for security
    res.json(users.map(({ id, username }) => ({ id, username })));
  }
});

// POST /users - Add new user (username only) for UI (no password, no auth)
app.post('/users', (req, res) => {
  const { username } = req.body;
  if (!username) return res.status(400).json({ error: "Username required" });
  if (users.find(u => u.username === username))
    return res.status(400).json({ error: "Username already exists" });

  // Password will be empty string, as this route doesn't require it
  users.push({ id: users.length + 1, username, password: "" });
  res.status(201).json({ id: users.length, username });
});

app.listen(3001, () => console.log("User Service on port 3001"));