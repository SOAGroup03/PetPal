const Pet = require('../models/Pet');

exports.createPet = async (req, res) => {
  const pet = new Pet({ ...req.body, owner: req.user.userId });
  await pet.save();
  res.status(201).json(pet);
};

exports.getUserPets = async (req, res) => {
  const pets = await Pet.find({ owner: req.user.userId });
  res.json(pets);
};

exports.getPetById = async (req, res) => {
  const pet = await Pet.findOne({ _id: req.params.id, owner: req.user.userId });
  if (!pet) return res.status(404).json({ error: 'Not found' });
  res.json(pet);
};

exports.updatePet = async (req, res) => {
  const pet = await Pet.findOneAndUpdate(
    { _id: req.params.id, owner: req.user.userId },
    req.body,
    { new: true }
  );
  res.json(pet);
};

exports.deletePet = async (req, res) => {
  await Pet.findOneAndDelete({ _id: req.params.id, owner: req.user.userId });
  res.json({ message: 'Deleted' });
};