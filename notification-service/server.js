const express = require("express");
const path = require("path");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from 'public'
app.use(express.static(path.join(__dirname, "public")));

let notifications = []; // In-memory store

// Redirect base URL to index.html
app.get("/", (req, res) => {
  res.redirect("/index.html");
});

// Get all notifications
app.get("/notifications", (req, res) => {
  res.json(notifications);
});

// Add a new notification
app.post("/notifications", (req, res) => {
  const { title, message, recipient } = req.body;
  if (!title || !message || !recipient) {
    return res.status(400).json({ error: "All fields are required" });
  }
  const newNotification = {
    id: notifications.length + 1,
    title,
    message,
    recipient,
    date: new Date().toISOString(),
  };
  notifications.push(newNotification);
  res.status(201).json(newNotification);
});

// Delete notification by id
app.delete("/notifications/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const index = notifications.findIndex((n) => n.id === id);
  if (index !== -1) {
    notifications.splice(index, 1);
    return res.status(204).send();
  }
  res.status(404).json({ error: "Notification not found" });
});

app.listen(3004, () => {
  console.log("Notification Service running on port 3004");
});
