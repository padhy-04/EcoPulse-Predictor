// backend/src/controllers/sensorController.js
const db = require('../models');

const sensorController = {
    async registerSensor(req, res) {
        const { sensorId, name, type, location } = req.body;
        if (!sensorId || !type) {
            return res.status(400).json({ message: 'Missing required fields: sensorId, type' });
        }

        try {
            const newSensor = await db.Sensor.create({
                sensorId,
                name: name || `Auto-generated ${type} Sensor`,
                type,
                location: location || null,
                status: 'active'
            });
            res.status(201).json({ message: 'Sensor registered successfully', sensor: newSensor });
        } catch (error) {
            if (error.name === 'SequelizeUniqueConstraintError') {
                return res.status(409).json({ message: `Sensor with ID '${sensorId}' already exists.` });
            }
            console.error('Error registering sensor:', error);
            res.status(500).json({ message: 'Failed to register sensor', error: error.message });
        }
    },

    async getAllSensors(req, res) {
        try {
            const sensors = await db.Sensor.findAll();
            res.status(200).json(sensors);
        } catch (error) {
            console.error('Error fetching sensors:', error);
            res.status(500).json({ message: 'Failed to retrieve sensors', error: error.message });
        }
    },

    async getSensorById(req, res) {
        try {
            const sensor = await db.Sensor.findByPk(req.params.id);
            if (!sensor) {
                return res.status(404).json({ message: 'Sensor not found' });
            }
            res.status(200).json(sensor);
        } catch (error) {
            console.error('Error fetching sensor by ID:', error);
            res.status(500).json({ message: 'Failed to retrieve sensor', error: error.message });
        }
    },

    async updateSensor(req, res) {
        const { id } = req.params;
        const { name, type, location, status } = req.body;
        try {
            const [updated] = await db.Sensor.update(
                { name, type, location, status },
                { where: { id } }
            );
            if (updated) {
                const updatedSensor = await db.Sensor.findByPk(id);
                return res.status(200).json({ message: 'Sensor updated successfully', sensor: updatedSensor });
            }
            throw new Error('Sensor not found or no changes applied');
        } catch (error) {
            console.error('Error updating sensor:', error);
            res.status(500).json({ message: 'Failed to update sensor', error: error.message });
        }
    },

    async deleteSensor(req, res) {
        const { id } = req.params;
        try {
            const deleted = await db.Sensor.destroy({ where: { id } });
            if (deleted) {
                return res.status(204).json({ message: 'Sensor deleted successfully' });
            }
            throw new Error('Sensor not found');
        } catch (error) {
            console.error('Error deleting sensor:', error);
            res.status(500).json({ message: 'Failed to delete sensor', error: error.message });
        }
    }
};

module.exports = sensorController;