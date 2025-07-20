const express = require("express");
const path = require("path");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from 'public'
app.use(express.static(path.join(__dirname, "public")));

let appointments = []; // In-memory DB

// Redirect base URL to index.html
app.get("/", (req, res) => {
  res.redirect("/index.html");
});

// Get all appointments
app.get("/appointments", (req, res) => {
  res.json(appointments);
});

// Add new appointment
app.post("/appointments", (req, res) => {
  const { petName, ownerName, date, reason } = req.body;
  if (!petName || !ownerName || !date || !reason) {
    return res.status(400).json({ error: "All fields are required" });
  }
  const newAppointment = {
    id: appointments.length + 1,
    petName,
    ownerName,
    date,
    reason,
  };
  appointments.push(newAppointment);
  res.status(201).json(newAppointment);
});

// Delete appointment by id
app.delete("/appointments/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const index = appointments.findIndex((a) => a.id === id);
  if (index !== -1) {
    appointments.splice(index, 1);
    return res.status(204).send();
  }
  res.status(404).json({ error: "Appointment not found" });
});

app.listen(3003, () => {
  console.log("Appointment Service running on port 3003");
});