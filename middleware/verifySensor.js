// middleware/verifySensor.js

const Sensor = require('../models/sensor');

module.exports = async (req, res, next) => {
  try {
    const sensorId = req.body.sensorId || req.params.sensorId;
    if (!sensorId) {
      return res.status(400).json({ success: false, message: 'Sensor ID is required' });
    }

    const sensor = await Sensor.findOne({ where: { id: sensorId } });
    if (!sensor) {
      return res.status(404).json({ success: false, message: 'Sensor not found' });
    }

    // Optionally attach sensor to request object for downstream use
    req.sensor = sensor;
    next();
  } catch (err) {
    next(err);
  }
};
