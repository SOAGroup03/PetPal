const express = require("express");
const router = express.Router();
const {
  register,
  login,
  getUsers,
  addUser,
} = require("../controllers/userController");

router.get("/users", getUsers);      // JSON data
router.post("/users", addUser);      // Add from UI
router.post("/register", register);  // Register with password
router.post("/login", login);        // Login + JWT

module.exports = router;