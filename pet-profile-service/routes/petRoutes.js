const express = require('express');
const router = express.Router();
const { createPet, getPetsByOwner, updatePet } = require('../controllers/petController');

router.post('/', createPet);
router.get('/:ownerId', getPetsByOwner);
router.put('/:id', updatePet);

module.exports = router;