// backend/src/controllers/dataController.js
const dbService = require('../services/db'); // Use the centralized DB service
const mlService = require('../services/mlService');

/**
 * @file dataController.js
 * @description Handles incoming sensor data, manages storage, and orchestrates anomaly detection via ML service.
 */

const dataController = {
    /**
     * Handles incoming sensor data, stores it, and sends it for anomaly detection.
     * This replaces the simpler `uploadData` from your snippet.
     * @param {Object} req - Express request object. Expected body: { sensor_id: string, timestamp: string, data: object }
     * @param {Object} res - Express response object.
     * @param {Function} next - Express next middleware function.
     */
    async receiveSensorData(req, res, next) {
        const { sensor_id: externalSensorId, timestamp, data } = req.body; // Renamed to externalSensorId for clarity

        if (!externalSensorId || !timestamp || !data) {
            return res.status(400).json({ message: 'Missing required fields: sensor_id, timestamp, data' });
        }

        try {
            // 1. Find the sensor by its externalSensorId to get its internal UUID
            const sensor = await dbService.models.Sensor.findOne({ where: { sensorId: externalSensorId } });
            if (!sensor) {
                // If sensor not found, it means it hasn't been registered.
                // In a real system, you might auto-register or reject the data.
                return res.status(404).json({ message: `Sensor with ID '${externalSensorId}' not found. Please register it first.` });
            }

            // 2. Store raw sensor data using the internal sensor UUID
            const newSensorData = await dbService.models.SensorData.create({
                sensorId: sensor.id, // Use the internal UUID from the Sensor model
                timestamp: new Date(timestamp),
                readings: data // Store the raw sensor readings as JSONB/object
            });
            console.log(`Sensor data from '${externalSensorId}' (internal ID: ${sensor.id}) saved. Data ID: ${newSensorData.id}`);

            // 3. Send data to ML service for anomaly detection
            const mlResponse = await mlService.detectAnomaly({
                sensor_id: externalSensorId, // Send external ID to ML service if it expects that
                timestamp,
                data
            });

            // 4. Process ML service response and store anomaly if detected
            if (mlResponse.is_anomaly) {
                await dbService.models.Anomaly.create({
                    sensorDataId: newSensorData.id, // Link to the raw sensor data record
                    sensorId: sensor.id, // Link to the Sensor record
                    timestamp: new Date(timestamp),
                    anomalyScore: mlResponse.anomaly_score,
                    detectedFeatures: mlResponse.monitored_features,
                    rawData: data, // Store the raw data that caused the anomaly
                    type: 'environmental_imbalance' // General type, can be refined based on features
                });
                console.warn(`Anomaly detected for sensor '${externalSensorId}'! Score: ${mlResponse.anomaly_score}`);
                // TODO: Integrate alerting system here (e.g., send email, SMS, push notification)
            } else {
                console.log(`No anomaly detected for sensor '${externalSensorId}'.`);
            }

            res.status(200).json({
                message: 'Sensor data received and processed',
                sensorDataId: newSensorData.id,
                anomalyStatus: mlResponse.is_anomaly,
                anomalyScore: mlResponse.anomaly_score
            });

        } catch (error) {
            console.error('Error processing sensor data:', error);
            next(error); // Pass error to centralized error handler
        }
    },

    /**
     * Retrieves all sensor data records, or filtered by sensor ID.
     * This replaces the simpler `getAllData` from your snippet.
     * @param {Object} req - Express request object. Supports query params `sensorId`.
     * @param {Object} res - Express response object.
     * @param {Function} next - Express next middleware function.
     */
    async getAllSensorData(req, res, next) {
        const { sensorId, startDate, endDate, limit, offset } = req.query; // sensorId here refers to the internal UUID or external
        let internalSensorId;

        try {
            if (sensorId) {
                // If sensorId is provided, first try to find the internal UUID
                const sensor = await dbService.models.Sensor.findOne({
                    where: { [dbService.models.Sequelize.Op.or]: [{ id: sensorId }, { sensorId: sensorId }] }
                });
                if (!sensor) {
                    return res.status(404).json({ message: `Sensor with ID '${sensorId}' not found.` });
                }
                internalSensorId = sensor.id;
            }

            const data = await dbService.getSensorData({
                sensorId: internalSensorId,
                startDate: startDate ? new Date(startDate) : undefined,
                endDate: endDate ? new Date(endDate) : undefined,
                limit: limit ? parseInt(limit, 10) : undefined,
                offset: offset ? parseInt(offset, 10) : undefined
            });
            res.status(200).json(data);
        } catch (error) {
            console.error('Error fetching all sensor data:', error);
            next(error); // Pass error to centralized error handler
        }
    },

    /**
     * Triggers ML model retraining through the ML service.
     * Fetches recent data from the database to send for training.
     * @param {Object} req - Express request object.
     * @param {Object} res - Express response object.
     * @param {Function} next - Express next middleware function.
     */
    async triggerModelRetrain(req, res, next) {
        try {
            // Fetch recent data for retraining (e.g., last 30 days)
            // You might want a more sophisticated way to select training data in production
            const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
            const historicalData = await dbService.models.SensorData.findAll({
                where: {
                    timestamp: {
                        [dbService.models.Sequelize.Op.gte]: thirtyDaysAgo
                    }
                },
                attributes: ['readings'] // Only send the actual sensor readings for ML
            });

            // Extract the 'readings' object from each entry
            const dataForML = historicalData.map(entry => entry.readings);

            if (dataForML.length === 0) {
                return res.status(400).json({ message: "No recent historical data found for retraining. Please ensure sensors are sending data." });
            }

            const mlResponse = await mlService.trainModel(dataForML);
            res.status(200).json({ message: 'ML model retraining initiated successfully', mlResponse });
        } catch (error) {
            console.error('Error triggering ML model retraining:', error);
            next(error); // Pass error to centralized error handler
        }
    }
};

module.exports = dataController;