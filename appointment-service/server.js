const express = require("express");
const app = express();
app.use(express.json());

let appointments = []; // mock DB

// Book appointment
app.post("/appointments", (req, res) => {
  const appt = { id: appointments.length + 1, ...req.body };
  appointments.push(appt);
  res.status(201).json(appt);
});

// Get appointments for a user
app.get("/appointments/:userId", (req, res) => {
  const userAppts = appointments.filter(a => a.userId === req.params.userId);
  res.json(userAppts);
});

app.listen(3003, () => console.log("Appointment Service on port 3003"));