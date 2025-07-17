const express = require("express");
const bodyParser = require("body-parser");
const cors = require("cors");
const path = require("path");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// In-memory database for appointments
const appointments = [];

// GET all appointments
app.get("/appointments", (req, res) => {
  res.json(appointments);
});

// POST new appointment
app.post("/appointments", (req, res) => {
  const { petName, ownerName, date, reason } = req.body;
  const newAppointment = {
    id: appointments.length + 1,
    petName,
    ownerName,
    date,
    reason
  };
  appointments.push(newAppointment);
  res.status(201).json(newAppointment);
});

// DELETE appointment by ID
app.delete("/appointments/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const index = appointments.findIndex(app => app.id === id);
  if (index !== -1) {
    appointments.splice(index, 1);
    res.status(204).send();
  } else {
    res.status(404).send("Appointment not found");
  }
});

// ✅ Match this with Docker (should be 3002 if you're exposing 3002)
app.listen(3003, () => {
  console.log("Appointment Service running on port 3002");
});
