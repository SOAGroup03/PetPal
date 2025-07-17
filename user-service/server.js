const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const app = express();
app.use(express.json());

const users = []; // temporary mock DB

// Registration
app.post("/register", async (req, res) => {
  const { username, password } = req.body;
  const hashed = await bcrypt.hash(password, 10);
  users.push({ id: users.length + 1, username, password: hashed });
  res.status(201).send("User registered");
});

// Login
app.post("/login", async (req, res) => {
  const { username, password } = req.body;
  const user = users.find((u) => u.username === username);
  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).send("Invalid credentials");
  }
  const token = jwt.sign({ userId: user.id }, "secretkey");
  res.json({ token });
});

// Serve decorated HTML page at /users when browser requests HTML
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
      <!-- Bootstrap CSS CDN -->
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
      <div class="container my-5">
        <h1 class="mb-4 text-primary">PetPal User Management</h1>

        <div class="mb-3">
          <label for="username" class="form-label">Add New User</label>
          <input type="text" class="form-control" id="username" placeholder="Enter user name" />
          <button class="btn btn-success mt-2" onclick="addUser()">Add User</button>
        </div>

        <h2 class="mt-5 mb-3">Users List</h2>
        <button class="btn btn-primary mb-3" onclick="fetchUsers()">Refresh Users</button>
        <ul id="usersList" class="list-group"></ul>
      </div>

      <script>
        async function addUser() {
          const nameInput = document.getElementById('username');
          const name = nameInput.value.trim();
          if (!name) {
            alert('Please enter a user name');
            return;
          }
          try {
            const res = await fetch('/users', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ name })
            });
            if (!res.ok) throw new Error('Failed to add user');
            const data = await res.json();
            alert('User added: ' + data.name + ' (ID: ' + data.id + ')');
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
                li.textContent = user.id + ': ' + user.name;
                list.appendChild(li);
              });
            }
          } catch (e) {
            alert(e.message);
          }
        }

        fetchUsers();
      </script>

      <!-- Bootstrap JS Bundle CDN (optional for Bootstrap features) -->
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    `);
  } else {
    // API clients get JSON
    res.json(users);
  }
});

// POST endpoint to add user (API)
app.post('/users', (req, res) => {
  const { name } = req.body;
  const newUser = { id: users.length + 1, name };
  users.push(newUser);
  res.status(201).json(newUser);
});

app.get('/users', (req, res) => {
  res.json(users);
});

app.listen(3001, () => console.log("User Service on port 3001"));