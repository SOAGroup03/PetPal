const Appointment = require('../models/Appointment');

exports.createAppointment = async (req, res) => {
  const appointment = new Appointment({ ...req.body, userId: req.user.userId });
  await appointment.save();
  res.status(201).json(appointment);
};

exports.getUserAppointments = async (req, res) => {
  const appointments = await Appointment.find({ userId: req.user.userId });
  res.json(appointments);
};

exports.getAppointmentById = async (req, res) => {
  const appointment = await Appointment.findOne({ _id: req.params.id, userId: req.user.userId });
  if (!appointment) return res.status(404).json({ error: 'Not found' });
  res.json(appointment);
};

exports.updateAppointment = async (req, res) => {
  const appointment = await Appointment.findOneAndUpdate(
    { _id: req.params.id, userId: req.user.userId },
    req.body,
    { new: true }
  );
  res.json(appointment);
};

exports.deleteAppointment = async (req, res) => {
  await Appointment.findOneAndDelete({ _id: req.params.id, userId: req.user.userId });
  res.json({ message: 'Deleted' });
};