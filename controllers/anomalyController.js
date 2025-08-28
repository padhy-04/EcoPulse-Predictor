// backend/src/controllers/anomalyController.js
const dbService = require('../services/db'); // Use the centralized DB service

/**
 * @file anomalyController.js
 * @description Handles requests for retrieving and managing detected anomalies.
 */

const anomalyController = {
    /**
     * Retrieves all detected anomalies, with optional filtering by status, sensor ID, and date range.
     * @param {Object} req - Express request object. Supports query params: `status`, `sensorId`, `startDate`, `endDate`.
     * @param {Object} res - Express response object.
     * @param {Function} next - Express next middleware function.
     */
    async getAllAnomalies(req, res, next) {
        const { status, sensorId, startDate, endDate } = req.query;

        try {
            // If sensorId is provided, convert external ID to internal UUID for filtering
            let internalSensorId;
            if (sensorId) {
                const sensor = await dbService.models.Sensor.findOne({
                    where: { [dbService.models.Sequelize.Op.or]: [{ id: sensorId }, { sensorId: sensorId }] }
                });
                if (!sensor) {
                    return res.status(404).json({ message: `Sensor with ID '${sensorId}' not found.` });
                }
                internalSensorId = sensor.id;
            }

            const anomalies = await dbService.getAnomalies({
                status,
                sensorId: internalSensorId,
                startDate: startDate ? new Date(startDate) : undefined,
                endDate: endDate ? new Date(endDate) : undefined
            });
            res.status(200).json(anomalies);
        } catch (error) {
            console.error('Error fetching anomalies:', error);
            next(error); // Pass error to centralized error handler
        }
    },

    /**
     * Retrieves a single anomaly record by its UUID.
     * @param {Object} req - Express request object. `req.params.id` is the anomaly UUID.
     * @param {Object} res - Express response object.
     * @param {Function} next - Express next middleware function.
     */
    async getAnomalyById(req, res, next) {
        try {
            const anomaly = await dbService.models.Anomaly.findByPk(req.params.id, {
                include: [{ model: dbService.models.Sensor, as: 'sensor', attributes: ['sensorId', 'name', 'type', 'location'] }]
            });
            if (!anomaly) {
                return res.status(404).json({ message: 'Anomaly not found' });
            }
            res.status(200).json(anomaly);
        } catch (error) {
            console.error('Error fetching anomaly by ID:', error);
            next(error); // Pass error to centralized error handler
        }
    },

    /**
     * Updates the status and/or notes of an anomaly record.
     * @param {Object} req - Express request object. `req.params.id` is the anomaly UUID. Body contains `status` and `notes`.
     * @param {Object} res - Express response object.
     * @param {Function} next - Express next middleware function.
     */
    async updateAnomalyStatus(req, res, next) {
        const { id } = req.params;
        const { status, notes } = req.body;

        const allowedStatuses = ['new', 'investigating', 'resolved', 'false_positive'];
        if (status && !allowedStatuses.includes(status)) { // Check if status is provided AND invalid
            return res.status(400).json({ message: 'Invalid status provided. Allowed: new, investigating, resolved, false_positive' });
        }

        try {
            const updateFields = {};
            if (status) updateFields.status = status;
            if (notes !== undefined) updateFields.notes = notes; // Allow notes to be cleared if explicitly set to null/empty

            const [updated] = await dbService.models.Anomaly.update(
                updateFields,
                { where: { id } }
            );

            if (updated) {
                const updatedAnomaly = await dbService.models.Anomaly.findByPk(id);
                return res.status(200).json({ message: 'Anomaly status updated successfully', anomaly: updatedAnomaly });
            }
            // If `updated` is 0, it means no rows were updated, likely because the ID wasn't found.
            return res.status(404).json({ message: 'Anomaly not found or no changes applied.' });

        } catch (error) {
            console.error('Error updating anomaly status:', error);
            next(error); // Pass error to centralized error handler
        }
    }
};

module.exports = anomalyController;