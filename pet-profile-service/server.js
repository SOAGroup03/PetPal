const express = require("express");
const path = require("path");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from 'public'
app.use(express.static(path.join(__dirname, "public")));

let pets = []; // In-memory DB for pet profiles

// Redirect base URL to index.html
app.get("/", (req, res) => {
  res.redirect("/index.html");
});

// Get all pet profiles
app.get("/pets", (req, res) => {
  res.json(pets);
});

// Add a new pet profile
app.post("/pets", (req, res) => {
  const { name, species, breed, age, ownerName } = req.body;
  if (!name || !species || !breed || !age || !ownerName) {
    return res.status(400).json({ error: "All fields are required" });
  }
  const newPet = {
    id: pets.length + 1,
    name,
    species,
    breed,
    age,
    ownerName,
  };
  pets.push(newPet);
  res.status(201).json(newPet);
});

// Delete pet profile by id
app.delete("/pets/:id", (req, res) => {
  const id = parseInt(req.params.id);
  const index = pets.findIndex((p) => p.id === id);
  if (index !== -1) {
    pets.splice(index, 1);
    return res.status(204).send();
  }
  res.status(404).json({ error: "Pet profile not found" });
});

app.listen(3002, () => {
  console.log("Pet Profile Service running on port 3002");
});