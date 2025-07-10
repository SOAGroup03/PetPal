const express = require("express");
const app = express();
app.use(express.json());

let pets = []; // temporary mock DB

// Add pet
app.post("/pets", (req, res) => {
  const pet = { id: pets.length + 1, ...req.body };
  pets.push(pet);
  res.status(201).json(pet);
});

// Get pets by owner ID
app.get("/pets/:ownerId", (req, res) => {
  const ownerPets = pets.filter(p => p.ownerId === req.params.ownerId);
  res.json(ownerPets);
});

app.listen(3002, () => console.log("Pet Profile Service on port 3002"));