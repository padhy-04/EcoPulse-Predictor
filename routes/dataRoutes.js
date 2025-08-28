// backend/src/routes/dataRoutes.js
const express = require('express');
const router = express.Router();
const dataController = require('../controllers/dataController');
// Import validation middleware
const { validateSensorDataIngestion, validateGetSensorDataQuery } = require('../utils/validation');

/**
 * @swagger
 * tags:
 * name: Sensor Data
 * description: APIs for collecting and processing sensor data
 */

/**
 * @swagger
 * /data/sensor-data:
 * post:
 * summary: Receive and process new sensor data
 * tags: [Sensor Data]
 * requestBody:
 * required: true
 * content:
 * application/json:
 * schema:
 * type: object
 * required:
 * - sensor_id
 * - timestamp
 * - data
 * properties:
 * sensor_id:
 * type: string
 * description: External ID of the sensor sending data.
 * example: "ESP32-Temp-001"
 * timestamp:
 * type: string
 * format: date-time
 * description: ISO 8601 timestamp of the reading.
 * example: "2025-07-05T14:30:00Z"
 * data:
 * type: object
 * description: Sensor readings (e.g., temperature, humidity, soil_ph).
 * example:
 * temperature: 28.5
 * humidity: 75.2
 * soil_ph: 6.7
 * water_turbidity: 15.0
 * responses:
 * 200:
 * description: Sensor data received and processed.
 * content:
 * application/json:
 * schema:
 * type: object
 * properties:
 * message:
 * type: string
 * example: "Sensor data received and processed"
 * sensorDataId:
 * type: string
 * format: uuid
 * example: "a1b2c3d4-e5f6-7890-1234-567890abcdef"
 * anomalyStatus:
 * type: boolean
 * example: false
 * anomalyScore:
 * type: number
 * format: float
 * example: 0.123
 * 400:
 * description: Missing required fields or invalid data format.
 * 404:
 * description: Sensor not found (if sensor_id provided is not registered).
 * 500:
 * description: Internal server error.
 */
router.post('/sensor-data', validateSensorDataIngestion, dataController.receiveSensorData);

/**
 * @swagger
 * /data/all:
 * get:
 * summary: Get all stored sensor data records
 * tags: [Sensor Data]
 * description: Retrieve all raw sensor data records. This endpoint might return a large dataset.
 * parameters:
 * - in: query
 * name: sensorId
 * schema:
 * type: string
 * description: Filter data by sensor internal UUID or external sensorId.
 * - in: query
 * name: startDate
 * schema:
 * type: string
 * format: date
 * description: Filter data starting from this ISO date (inclusive).
 * - in: query
 * name: endDate
 * schema:
 * type: string
 * format: date
 * description: Filter data up to this ISO date (inclusive).
 * - in: query
 * name: limit
 * schema:
 * type: integer
 * minimum: 1
 * maximum: 100
 * default: 20
 * description: Number of records to return per page.
 * - in: query
 * name: offset
 * schema:
 * type: integer
 * minimum: 0
 * default: 0
 * description: Number of records to skip for pagination.
 * responses:
 * 200:
 * description: A list of all sensor data records.
 * content:
 * application/json:
 * schema:
 * type: array
 * items:
 * $ref: '#/components/schemas/SensorData' # Assuming SensorData schema defined elsewhere
 * 400:
 * description: Invalid query parameters.
 * 500:
 * description: Internal server error.
 */
router.get('/all', validateGetSensorDataQuery, dataController.getAllSensorData);

/**
 * @swagger
 * /data/retrain-model:
 * post:
 * summary: Trigger ML model retraining
 * tags: [Sensor Data]
 * description: Initiates a process to retrain the anomaly detection ML model using historical data.
 * This may fetch data from the database.
 * responses:
 * 200:
 * description: ML model retraining initiated successfully.
 * content:
 * application/json:
 * schema:
 * type: object
 * properties:
 * message:
 * type: string
 * example: "ML model retraining initiated"
 * mlResponse:
 * type: object
 * description: Response from the ML service regarding retraining.
 * 400:
 * description: No recent historical data found for retraining.
 * 500:
 * description: Internal server error.
 */
router.post('/retrain-model', dataController.triggerModelRetrain); // No specific body validation for retraining assumed for now

module.exports = router;