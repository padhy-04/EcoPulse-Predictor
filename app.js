// backend/src/app.js
const express = require('express');
const sensorRoutes = require('./routes/sensorRoutes');
const dataRoutes = require('./routes/dataRoutes');
const anomalyRoutes = require('./routes/anomalyRoutes');
const errorHandler = require('./middleware/errorHandler'); // Assuming this middleware exists and handles errors
require('dotenv').config(); // Load environment variables from .env file

const app = express();

// Middleware to parse JSON bodies from incoming requests
app.use(express.json());

// Basic health check or root endpoint
app.get('/', (req, res) => {
    res.send('Ecosystem Health & Biodiversity Monitoring Platform API is running!');
});

// Mount API routes
// All routes defined in sensorRoutes will be prefixed with /api/sensors
app.use('/api/sensors', sensorRoutes);
// All routes defined in dataRoutes will be prefixed with /api/data
app.use('/api/data', dataRoutes);
// All routes defined in anomalyRoutes will be prefixed with /api/anomalies
app.use('/api/anomalies', anomalyRoutes);

// Catch-all middleware for any requests to undefined routes (404 Not Found)
// This should be placed after all defined routes but before the error handler
app.use((req, res, next) => {
    const error = new Error(`Not Found - ${req.originalUrl}`);
    res.status(404);
    next(error); // Pass the error to the next middleware (our errorHandler)
});

// Centralized error handling middleware
// This should be the last middleware in the chain
app.use(errorHandler);

module.exports = app;