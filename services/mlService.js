// backend/src/services/mlService.js
const axios = require('axios'); // Ensure axios is installed: npm install axios

// Load ML_SERVICE_URL from environment variables
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:5001'; // Default to localhost:5001 if not set

/**
 * @file mlService.js
 * @description Service for communicating with the Python ML microservice.
 * Handles requests for anomaly detection and model retraining.
 */

const mlService = {
    /**
     * Sends sensor data to the ML microservice for anomaly detection.
     * @param {object} sensorDataPayload - The sensor data object to be analyzed.
     * Expected format: { sensor_id: "...", timestamp: "...", data: { ... } }
     * @returns {Promise<object>} - A promise that resolves with the ML service's response.
     * Expected response: { is_anomaly: boolean, anomaly_score: number, monitored_features: [] }
     */
    async detectAnomaly(sensorDataPayload) {
        try {
            const response = await axios.post(`${ML_SERVICE_URL}/detect-anomaly`, sensorDataPayload);
            return response.data;
        } catch (error) {
            console.error('ML Service Error: Anomaly detection failed.');
            console.error('Request Payload:', sensorDataPayload);
            if (error.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                console.error('ML Service Response Error Data:', error.response.data);
                console.error('ML Service Response Status:', error.response.status);
                console.error('ML Service Response Headers:', error.response.headers);
                throw new Error(`ML service anomaly detection failed: ${error.response.data.error || error.response.statusText}`);
            } else if (error.request) {
                // The request was made but no response was received
                console.error('ML Service No Response Received:', error.request);
                throw new Error('ML service did not respond. Is it running?');
            } else {
                // Something happened in setting up the request that triggered an Error
                console.error('ML Service Request Setup Error:', error.message);
                throw new Error(`Error setting up ML service request: ${error.message}`);
            }
        }
    },

    /**
     * Triggers retraining of the ML model with historical data.
     * @param {Array<object>} historicalData - An array of historical sensor data readings (e.g., [{ temperature: 25, humidity: 60 }, ...]).
     * @returns {Promise<object>} - A promise that resolves with the ML service's response.
     */
    async trainModel(historicalData) {
        try {
            const response = await axios.post(`${ML_SERVICE_URL}/train-model`, { historical_data: historicalData });
            return response.data;
        } catch (error) {
            console.error('ML Service Error: Model training failed.');
            // Detailed error logging similar to detectAnomaly
            if (error.response) {
                console.error('ML Service Response Error Data:', error.response.data);
                throw new Error(`ML service model training failed: ${error.response.data.error || error.response.statusText}`);
            } else if (error.request) {
                throw new Error('ML service did not respond for training. Is it running?');
            } else {
                throw new Error(`Error setting up ML service training request: ${error.message}`);
            }
        }
    },

    /**
     * Checks the health of the ML service.
     * @returns {Promise<boolean>} - True if the ML service is healthy, false otherwise.
     */
    async checkHealth() {
        try {
            const response = await axios.get(`${ML_SERVICE_URL}/health`);
            // Check for a 200 status and a specific 'ok' status from the service
            return response.status === 200 && response.data.status === 'ok';
        } catch (error) {
            console.error('ML Service Health check failed:', error.message);
            return false;
        }
    }
};

module.exports = mlService;