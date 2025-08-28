// backend/src/routes/anomalyRoutes.js
const express = require('express');
const router = express.Router();
const anomalyController = require('../controllers/anomalyController');
// Import validation middleware
const { validateGetAnomaliesQuery, validateUpdateAnomalyStatus, validateIdParam } = require('../utils/validation');

/**
 * @swagger
 * tags:
 * name: Anomalies
 * description: APIs for accessing and managing detected anomalies
 */

/**
 * @swagger
 * /anomalies:
 * get:
 * summary: Get all detected anomalies
 * tags: [Anomalies]
 * parameters:
 * - in: query
 * name: status
 * schema:
 * type: string
 * enum: [new, investigating, resolved, false_positive]
 * description: Filter anomalies by status.
 * - in: query
 * name: sensorId
 * schema:
 * type: string
 * format: uuid
 * description: Filter anomalies by internal sensor UUID or external sensorId.
 * - in: query
 * name: startDate
 * schema:
 * type: string
 * format: date
 * description: Filter anomalies detected after this date (YYYY-MM-DD).
 * - in: query
 * name: endDate
 * schema:
 * type: string
 * format: date
 * description: Filter anomalies detected before this date (YYYY-MM-DD).
 * - in: query
 * name: limit
 * schema:
 * type: integer
 * minimum: 1
 * maximum: 100
 * default: 20
 * description: Number of anomalies to return per page.
 * - in: query
 * name: offset
 * schema:
 * type: integer
 * minimum: 0
 * default: 0
 * description: Number of anomalies to skip for pagination.
 * responses:
 * 200:
 * description: A list of detected anomalies.
 * content:
 * application/json:
 * schema:
 * type: array
 * items:
 * $ref: '#/components/schemas/Anomaly' # Assuming Anomaly schema defined elsewhere
 * 400:
 * description: Invalid query parameters.
 * 500:
 * description: Internal server error.
 */
router.get('/', validateGetAnomaliesQuery, anomalyController.getAllAnomalies);

/**
 * @swagger
 * /anomalies/{id}:
 * get:
 * summary: Get an anomaly by its internal UUID
 * tags: [Anomalies]
 * parameters:
 * - in: path
 * name: id
 * schema:
 * type: string
 * format: uuid
 * required: true
 * description: The anomaly's internal UUID.
 * responses:
 * 200:
 * description: Anomaly details.
 * content:
 * application/json:
 * schema:
 * $ref: '#/components/schemas/Anomaly'
 * 400:
 * description: Invalid ID format.
 * 404:
 * description: Anomaly not found.
 * 500:
 * description: Internal server error.
 */
router.get('/:id', validateIdParam, anomalyController.getAnomalyById);

/**
 * @swagger
 * /anomalies/{id}/status:
 * patch:
 * summary: Update the status of an anomaly
 * tags: [Anomalies]
 * parameters:
 * - in: path
 * name: id
 * schema:
 * type: string
 * format: uuid
 * required: true
 * description: The anomaly's internal UUID.
 * requestBody:
 * required: true
 * content:
 * application/json:
 * schema:
 * type: object
 * required:
 * - status
 * properties:
 * status:
 * type: string
 * enum: [new, investigating, resolved, false_positive]
 * description: New status for the anomaly.
 * notes:
 * type: string
 * description: Additional notes for the status update.
 * responses:
 * 200:
 * description: Anomaly status updated successfully.
 * 400:
 * description: Invalid status provided or invalid ID format.
 * 404:
 * description: Anomaly not found.
 * 500:
 * description: Internal server error.
 */
router.patch('/:id/status', validateIdParam, validateUpdateAnomalyStatus, anomalyController.updateAnomalyStatus);

module.exports = router;