const express = require('express');
const router = express.Router();
const petController = require('../controllers/petController');
const auth = require('../middleware/auth');

router.post('/', auth, petController.createPet);
router.get('/', auth, petController.getUserPets);
router.get('/:id', auth, petController.getPetById);
router.put('/:id', auth, petController.updatePet);
router.delete('/:id', auth, petController.deletePet);

module.exports = router;