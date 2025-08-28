// backend/src/services/db.js
const db = require('../models'); // Import the already configured db object from models/index.js

/**
 * @file db.js
 * @description Centralized access point for database models and higher-level database operations.
 * This service wraps direct model access, providing a cleaner interface for other services.
 */

const dbService = {
    /**
     * Access to all Sequelize models.
     * Example: dbService.models.Sensor.findAll()
     */
    models: db,

    /**
     * Fetches sensor data records, optionally filtered by sensor ID and time range.
     * @param {object} options - Options for fetching data.
     * @param {string} [options.sensorId] - The UUID of the sensor.
     * @param {Date} [options.startDate] - Start date for data (inclusive).
     * @param {Date} [options.endDate] - End date for data (inclusive).
     * @param {number} [options.limit] - Max number of records to return.
     * @param {number} [options.offset] - Offset for pagination.
     * @returns {Promise<Array<object>>} A promise that resolves with an array of sensor data records.
     */
    async getSensorData(options = {}) {
        const { Op } = db.Sequelize; // Access Sequelize operators
        const whereClause = {};

        if (options.sensorId) {
            whereClause.sensorId = options.sensorId;
        }
        if (options.startDate || options.endDate) {
            whereClause.timestamp = {};
            if (options.startDate) {
                whereClause.timestamp[Op.gte] = options.startDate;
            }
            if (options.endDate) {
                whereClause.timestamp[Op.lte] = options.endDate;
            }
        }

        try {
            const data = await db.SensorData.findAll({
                where: whereClause,
                limit: options.limit,
                offset: options.offset,
                order: [['timestamp', 'DESC']], // Latest data first
                include: [{
                    model: db.Sensor,
                    as: 'sensor',
                    attributes: ['sensorId', 'name', 'type', 'location']
                }]
            });
            return data.map(record => record.toJSON()); // Return plain JSON objects
        } catch (error) {
            console.error('DB Service Error: Failed to fetch sensor data:', error);
            throw new Error('Could not retrieve sensor data.');
        }
    },

    /**
     * Fetches detected anomalies, optionally filtered by status, sensor ID, and time range.
     * @param {object} options - Options for fetching anomalies.
     * @param {string} [options.status] - Filter by anomaly status (e.g., 'new', 'resolved').
     * @param {string} [options.sensorId] - The UUID of the sensor.
     * @param {Date} [options.startDate] - Start date for anomaly detection (inclusive).
     * @param {Date} [options.endDate] - End date for anomaly detection (inclusive).
     * @returns {Promise<Array<object>>} A promise that resolves with an array of anomaly records.
     */
    async getAnomalies(options = {}) {
        const { Op } = db.Sequelize;
        const whereClause = {};

        if (options.status) {
            whereClause.status = options.status;
        }
        if (options.sensorId) {
            whereClause.sensorId = options.sensorId;
        }
        if (options.startDate || options.endDate) {
            whereClause.timestamp = {};
            if (options.startDate) {
                whereClause.timestamp[Op.gte] = options.startDate;
            }
            if (options.endDate) {
                whereClause.timestamp[Op.lte] = options.endDate;
            }
        }

        try {
            const anomalies = await db.Anomaly.findAll({
                where: whereClause,
                order: [['timestamp', 'DESC']],
                include: [{
                    model: db.Sensor,
                    as: 'sensor',
                    attributes: ['sensorId', 'name', 'type', 'location']
                }]
            });
            return anomalies.map(record => record.toJSON());
        } catch (error) {
            console.error('DB Service Error: Failed to fetch anomalies:', error);
            throw new Error('Could not retrieve anomalies.');
        }
    },

    /**
     * Creates a new sensor record.
     * @param {object} sensorData - Data for the new sensor.
     * @returns {Promise<object>} A promise that resolves with the created sensor record.
     */
    async createSensor(sensorData) {
        try {
            const newSensor = await db.Sensor.create(sensorData);
            return newSensor.toJSON();
        } catch (error) {
            console.error('DB Service Error: Failed to create sensor:', error);
            throw error; // Re-throw to allow specific error handling (e.g., unique constraint)
        }
    },

    // You can add more higher-level DB operations here, e.g.:
    // async updateSensor(id, data) { ... }
    // async deleteSensor(id) { ... }
    // async updateAnomalyStatus(id, newStatus, notes) { ... }
};

module.exports = dbService;