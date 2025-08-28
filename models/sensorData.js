// backend/src/models/sensorData.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database'); // Adjust path if needed
const Sensor = require('./sensor'); // Import the Sensor model

const SensorData = sequelize.define('SensorData', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
        allowNull: false,
        comment: 'Unique identifier for the sensor data record'
    },
    sensorId: { // Foreign key to the Sensor model
        type: DataTypes.UUID, // Assuming Sensor.id is UUID
        allowNull: false,
        references: {
            model: Sensor,
            key: 'id',
        },
        comment: 'Foreign key to the Sensor model, linking data to a specific sensor'
    },
    timestamp: {
        type: DataTypes.DATE,
        allowNull: false,
        comment: 'Timestamp when the sensor reading was taken'
    },
    readings: {
        type: DataTypes.JSONB, // Use JSONB for flexible storage of various sensor readings
        allowNull: false,
        comment: 'JSON object containing key-value pairs of sensor readings (e.g., { "temperature": 25.5, "humidity": 60, "soil_ph": 7.2 })'
    },
    // Potentially add rawDataLink for large files like images/audio, or processedData for ML features
}, {
    tableName: 'sensor_data', // Explicitly define table name
    timestamps: true,         // Adds createdAt and updatedAt columns
    comment: 'Table to store raw time-series data collected from sensors'
});

// Define association: A SensorData record belongs to one Sensor
SensorData.belongsTo(Sensor, { foreignKey: 'sensorId', as: 'sensor' });
// A Sensor can have many SensorData records
Sensor.hasMany(SensorData, { foreignKey: 'sensorId', as: 'data' });


module.exports = SensorData;