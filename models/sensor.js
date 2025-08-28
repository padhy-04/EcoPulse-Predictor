// backend/src/models/sensor.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database'); // Adjust path if needed

const Sensor = sequelize.define('Sensor', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
        allowNull: false,
        comment: 'Unique identifier for the sensor'
    },
    sensorId: {
        type: DataTypes.STRING,
        allowNull: false,
        unique: true, // Each sensor should have a unique ID
        comment: 'External ID or identifier for the physical sensor device'
    },
    name: {
        type: DataTypes.STRING,
        allowNull: true,
        comment: 'Human-readable name for the sensor (e.g., "River pH Sensor 1")'
    },
    type: {
        type: DataTypes.STRING,
        allowNull: false,
        comment: 'Type of sensor (e.g., "temperature", "humidity", "soil_ph", "water_quality", "camera", "audio")'
    },
    location: {
        type: DataTypes.JSONB, // Store latitude, longitude, and potentially description
        allowNull: true,
        comment: 'Geographic location of the sensor (e.g., { "latitude": 20.123, "longitude": 84.567, "description": "Near old bridge" })'
    },
    status: {
        type: DataTypes.STRING,
        allowNull: false,
        defaultValue: 'active', // e.g., 'active', 'inactive', 'maintenance', 'faulty'
        comment: 'Current operational status of the sensor'
    },
    lastCommunication: {
        type: DataTypes.DATE,
        allowNull: true,
        comment: 'Timestamp of the last successful data transmission from the sensor'
    },
    // Potentially add more fields like battery level, installation date, notes, etc.
}, {
    tableName: 'sensors', // Explicitly define table name
    timestamps: true,     // Adds createdAt and updatedAt columns
    comment: 'Table to store information about deployed environmental sensors'
});

module.exports = Sensor;