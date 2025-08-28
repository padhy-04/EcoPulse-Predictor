// backend/src/utils/validation.js
const Joi = require('joi');

/**
 * @file validation.js
 * @description Centralized Joi schemas and validation functions for API requests.
 */

// --- Joi Schemas ---

// Schema for sensor location data
const locationSchema = Joi.object({
    latitude: Joi.number().min(-90).max(90).required(),
    longitude: Joi.number().min(-180).max(180).required(),
    description: Joi.string().trim().min(3).max(255).optional().allow(null, ''),
});

// Schema for sensor registration data (POST /api/sensors)
const registerSensorSchema = Joi.object({
    sensorId: Joi.string().trim().min(3).max(100).required()
        .description('Unique external identifier for the physical sensor device.'),
    name: Joi.string().trim().min(3).max(255).optional().allow(null, '')
        .description('Human-readable name for the sensor.'),
    type: Joi.string().trim().min(2).max(50).required()
        .description('Type of sensor (e.g., "temperature", "humidity", "water_quality", "camera").'),
    location: locationSchema.optional().allow(null)
        .description('Geographic location details of the sensor.'),
    // Status can be set by default in the model, or validated if provided in initial registration
    status: Joi.string().valid('active', 'inactive', 'maintenance', 'faulty').optional().default('active')
        .description('Current operational status of the sensor.'),
});

// Schema for updating sensor data (PUT /api/sensors/:id)
const updateSensorSchema = Joi.object({
    name: Joi.string().trim().min(3).max(255).optional(),
    type: Joi.string().trim().min(2).max(50).optional(),
    location: locationSchema.optional().allow(null),
    status: Joi.string().valid('active', 'inactive', 'maintenance', 'faulty').optional(),
}).min(1) // At least one field must be provided for update
  .description('Schema for updating an existing sensor.');


// Schema for incoming sensor data (POST /api/data/sensor-data)
const sensorDataIngestionSchema = Joi.object({
    sensor_id: Joi.string().trim().min(3).max(100).required()
        .description('The external ID of the sensor sending the data.'),
    timestamp: Joi.date().iso().required()
        .description('ISO 8601 timestamp of the sensor reading.'),
    data: Joi.object().min(1).pattern(
        Joi.string().trim().min(1), // Key: e.g., "temperature", "humidity"
        Joi.alternatives().try(Joi.number(), Joi.string(), Joi.boolean()) // Value: can be number, string, boolean
    ).required()
     .description('JSON object containing key-value pairs of sensor readings.'),
}).description('Schema for validating incoming sensor data payload.');

// Schema for query parameters when getting sensor data (GET /api/data/all)
const getSensorDataQuerySchema = Joi.object({
    sensorId: Joi.string().trim().optional() // Can be internal UUID or external sensorId
        .description('Filter data by sensor internal UUID or external sensorId.'),
    startDate: Joi.date().iso().optional()
        .description('Filter data starting from this ISO date (inclusive).'),
    endDate: Joi.date().iso().optional()
        .description('Filter data up to this ISO date (inclusive).'),
    limit: Joi.number().integer().min(1).max(100).default(20)
        .description('Number of records to return per page.'),
    offset: Joi.number().integer().min(0).default(0)
        .description('Number of records to skip for pagination.'),
}).description('Schema for query parameters when fetching sensor data.');


// Schema for updating anomaly status (PATCH /api/anomalies/:id/status)
const updateAnomalyStatusSchema = Joi.object({
    status: Joi.string().valid('new', 'investigating', 'resolved', 'false_positive').required()
        .description('New status for the anomaly.'),
    notes: Joi.string().trim().max(1000).optional().allow(null, '')
        .description('Additional notes for the anomaly status update.'),
}).description('Schema for updating anomaly status.');

// Schema for query parameters when getting anomalies (GET /api/anomalies)
const getAnomaliesQuerySchema = Joi.object({
    status: Joi.string().valid('new', 'investigating', 'resolved', 'false_positive').optional()
        .description('Filter anomalies by status.'),
    sensorId: Joi.string().trim().optional() // Can be internal UUID or external sensorId
        .description('Filter anomalies by sensor internal UUID or external sensorId.'),
    startDate: Joi.date().iso().optional()
        .description('Filter anomalies detected after this ISO date (inclusive).'),
    endDate: Joi.date().iso().optional()
        .description('Filter anomalies detected before this ISO date (inclusive).'),
    limit: Joi.number().integer().min(1).max(100).default(20)
        .description('Number of anomalies to return per page.'),
    offset: Joi.number().integer().min(0).default(0)
        .description('Number of anomalies to skip for pagination.'),
}).description('Schema for query parameters when fetching anomalies.');


// --- Validation Middleware Factory ---

/**
 * Creates a validation middleware for Express routes.
 * @param {Joi.Schema} schema - The Joi schema to validate against.
 * @param {string} property - The property of the request object to validate ('body', 'query', 'params').
 * @returns {Function} Express middleware function.
 */
const validate = (schema, property) => (req, res, next) => {
    const { error, value } = schema.validate(req[property], { abortEarly: false, allowUnknown: true });
    // `allowUnknown: true` allows unknown keys, useful if you only want to validate specific fields
    // If you want to strictly forbid unknown keys, set `allowUnknown: false`
    
    if (error) {
        // Map validation errors into a more readable format
        const errors = error.details.map(detail => ({
            field: detail.context.key,
            message: detail.message
        }));
        return res.status(400).json({
            message: 'Validation failed',
            errors: errors
        });
    }
    // If validation is successful, replace the original property with the validated value
    // This removes unknown fields and applies defaults/type conversions if defined in schema.
    req[property] = value; 
    next();
};

// --- Specific Validation Middleware Exports ---

exports.validateRegisterSensor = validate(registerSensorSchema, 'body');
exports.validateUpdateSensor = validate(updateSensorSchema, 'body');
exports.validateSensorDataIngestion = validate(sensorDataIngestionSchema, 'body');
exports.validateGetSensorDataQuery = validate(getSensorDataQuerySchema, 'query');
exports.validateUpdateAnomalyStatus = validate(updateAnomalyStatusSchema, 'body');
exports.validateGetAnomaliesQuery = validate(getAnomaliesQuerySchema, 'query');

// Generic UUID validation middleware for path parameters
// Note: Joi.string().guid({ version: 'uuidv4' }) is better for specific UUID versions
exports.validateIdParam = (req, res, next) => {
    const schema = Joi.string().guid({ version: ['uuidv4', 'uuidv5'] }).required(); // Assuming UUIDv4 or UUIDv5
    const { error } = schema.validate(req.params.id);

    if (error) {
        return res.status(400).json({
            message: 'Invalid ID format',
            errors: [{ field: 'id', message: 'ID must be a valid UUID' }]
        });
    }
    next();
};