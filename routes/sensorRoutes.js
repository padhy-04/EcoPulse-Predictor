// backend/src/routes/sensorRoutes.js
const express = require('express');
const router = express.Router();
const sensorController = require('../controllers/sensorController');
// Import validation middleware
const { validateRegisterSensor, validateUpdateSensor, validateIdParam } = require('../utils/validation');

/**
 * @swagger
 * tags:
 * name: Sensors
 * description: Sensor management APIs
 */

/**
 * @swagger
 * /sensors:
 * post:
 * summary: Register a new sensor
 * tags: [Sensors]
 * requestBody:
 * required: true
 * content:
 * application/json:
 * schema:
 * type: object
 * required:
 * - sensorId
 * - type
 * properties:
 * sensorId:
 * type: string
 * description: Unique identifier for the physical sensor device.
 * example: "ESP32-Temp-001"
 * name:
 * type: string
 * description: Human-readable name for the sensor.
 * example: "Outdoor Temperature Sensor"
 * type:
 * type: string
 * description: Type of sensor (e.g., "temperature", "humidity", "soil_ph", "water_quality", "camera", "audio").
 * example: "temperature"
 * location:
 * type: object
 * properties:
 * latitude:
 * type: number
 * longitude:
 * type: number
 * description:
 * type: string
 * description: Geographic location of the sensor.
 * example: { "latitude": 20.123, "longitude": 84.567, "description": "Near old bridge" }
 * responses:
 * 201:
 * description: Sensor registered successfully.
 * content:
 * application/json:
 * schema:
 * type: object
 * properties:
 * message:
 * type: string
 * example: "Sensor registered successfully"
 * sensor:
 * $ref: '#/components/schemas/Sensor' # Assuming Sensor schema defined elsewhere
 * 400:
 * description: Missing required fields or invalid data.
 * 409:
 * description: Sensor with given ID already exists.
 * 500:
 * description: Internal server error.
 */
router.post('/', validateRegisterSensor, sensorController.registerSensor);

/**
 * @swagger
 * /sensors:
 * get:
 * summary: Get all registered sensors
 * tags: [Sensors]
 * responses:
 * 200:
 * description: A list of sensors.
 * content:
 * application/json:
 * schema:
 * type: array
 * items:
 * $ref: '#/components/schemas/Sensor'
 * 500:
 * description: Internal server error.
 */
router.get('/', sensorController.getAllSensors);

/**
 * @swagger
 * /sensors/{id}:
 * get:
 * summary: Get a sensor by its internal UUID
 * tags: [Sensors]
 * parameters:
 * - in: path
 * name: id
 * schema:
 * type: string
 * format: uuid
 * required: true
 * description: The sensor's internal UUID.
 * responses:
 * 200:
 * description: Sensor details.
 * content:
 * application/json:
 * schema:
 * $ref: '#/components/schemas/Sensor'
 * 400:
 * description: Invalid ID format.
 * 404:
 * description: Sensor not found.
 * 500:
 * description: Internal server error.
 */
router.get('/:id', validateIdParam, sensorController.getSensorById);

/**
 * @swagger
 * /sensors/{id}:
 * put:
 * summary: Update an existing sensor by its internal UUID
 * tags: [Sensors]
 * parameters:
 * - in: path
 * name: id
 * schema:
 * type: string
 * format: uuid
 * required: true
 * description: The sensor's internal UUID.
 * requestBody:
 * required: true
 * content:
 * application/json:
 * schema:
 * type: object
 * properties:
 * name:
 * type: string
 * type:
 * type: string
 * location:
 * type: object
 * status:
 * type: string
 * responses:
 * 200:
 * description: Sensor updated successfully.
 * 400:
 * description: Invalid ID format or invalid update data.
 * 404:
 * description: Sensor not found.
 * 500:
 * description: Internal server error.
 */
router.put('/:id', validateIdParam, validateUpdateSensor, sensorController.updateSensor);

/**
 * @swagger
 * /sensors/{id}:
 * delete:
 * summary: Delete a sensor by its internal UUID
 * tags: [Sensors]
 * parameters:
 * - in: path
 * name: id
 * schema:
 * type: string
 * format: uuid
 * required: true
 * description: The sensor's internal UUID.
 * responses:
 * 204:
 * description: Sensor deleted successfully.
 * 400:
 * description: Invalid ID format.
 * 404:
 * description: Sensor not found.
 * 500:
 * description: Internal server error.
 */
router.delete('/:id', validateIdParam, sensorController.deleteSensor);

module.exports = router;