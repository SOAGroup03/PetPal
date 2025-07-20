const Notification = require('../models/Notification');

exports.createNotification = async (req, res) => {
  const notification = new Notification({
    ...req.body,
    userId: req.user.userId
  });
  await notification.save();
  res.status(201).json(notification);
};

exports.getUserNotifications = async (req, res) => {
  const notifications = await Notification.find({ userId: req.user.userId });
  res.json(notifications);
};

exports.deleteNotification = async (req, res) => {
  await Notification.findOneAndDelete({ _id: req.params.id, userId: req.user.userId });
  res.json({ message: 'Deleted' });
};