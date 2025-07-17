const mongoose = require('mongoose');

const petSchema = new mongoose.Schema({
  ownerId: { type: mongoose.Schema.Types.ObjectId, required: true },
  name: String,
  type: String,
  breed: String,
  age: Number,
  vaccinations: [String],
  medicalHistory: [String],
});

module.exports = mongoose.model('Pet', petSchema);