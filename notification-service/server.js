const express = require("express");
const app = express();
app.use(express.json());

// Send email
app.post("/notify/email", (req, res) => {
  const { email, message } = req.body;
  console.log(`Sending email to ${email}: ${message}`);
  res.send("Email notification sent");
});

// Send SMS
app.post("/notify/sms", (req, res) => {
  const { phone, message } = req.body;
  console.log(`Sending SMS to ${phone}: ${message}`);
  res.send("SMS notification sent");
});

app.listen(3004, () => console.log("Notification Service on port 3004"));
