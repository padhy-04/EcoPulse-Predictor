// backend/src/models/anomaly.js
const { DataTypes } = require('sequelize');
const sequelize = require('../config/database'); // Adjust path if needed
const SensorData = require('./sensorData'); // Import SensorData model
const Sensor = require('./sensor');         // Import Sensor model

const Anomaly = sequelize.define('Anomaly', {
    id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
        allowNull: false,
        comment: 'Unique identifier for the anomaly record'
    },
    sensorDataId: {
        type: DataTypes.UUID,
        allowNull: true, // Allow null if anomaly is detected without specific raw data record (e.g., aggregate anomaly)
        references: {
            model: SensorData, // Foreign key to SensorData
            key: 'id',
        },
        comment: 'Foreign key to the SensorData record that triggered this anomaly, if applicable'
    },
    sensorId: { // Redundant but useful for quick queries and if sensorDataId is null
        type: DataTypes.UUID, // Assuming Sensor.id is UUID
        allowNull: false,
        references: {
            model: Sensor,
            key: 'id',
        },
        comment: 'Foreign key to the Sensor model associated with the anomaly'
    },
    timestamp: {
        type: DataTypes.DATE,
        allowNull: false,
        comment: 'Timestamp when the anomaly was detected'
    },
    anomalyScore: {
        type: DataTypes.FLOAT,
        allowNull: false,
        comment: 'Score indicating the degree of anomaly (e.g., Isolation Forest decision_function output)'
    },
    type: {
        type: DataTypes.STRING,
        allowNull: true, // e.g., 'temperature_spike', 'low_ph', 'sensor_malfunction', 'biodiversity_change'
        comment: 'Categorization of the anomaly type'
    },
    detectedFeatures: {
        type: DataTypes.ARRAY(DataTypes.STRING), // List of features that contributed most to the anomaly
        allowNull: true,
        comment: 'Array of feature names that were most indicative of the anomaly'
    },
    rawData: {
        type: DataTypes.JSONB, // Store the specific raw data values that caused the anomaly
        allowNull: true,
        comment: 'JSON object of the sensor readings when the anomaly was detected'
    },
    status: {
        type: DataTypes.STRING,
        allowNull: false,
        defaultValue: 'new', // e.g., 'new', 'investigating', 'resolved', 'false_positive'
        comment: 'Current status of the anomaly investigation'
    },
    notes: {
        type: DataTypes.TEXT,
        allowNull: true,
        comment: 'Additional notes or comments about the anomaly'
    }
}, {
    tableName: 'anomalies', // Explicitly define table name
    timestamps: true,       // Adds createdAt and updatedAt columns
    comment: 'Table to store detected anomalies from ML models'
});

// Define associations:
// An Anomaly can belong to one SensorData record (optional)
Anomaly.belongsTo(SensorData, { foreignKey: 'sensorDataId', as: 'sensor_data' });
// A SensorData record can have one Anomaly (or more if multiple types of anomalies are tracked for one reading)
SensorData.hasOne(Anomaly, { foreignKey: 'sensorDataId', as: 'anomaly', onDelete: 'SET NULL' }); // If sensorData is deleted, anomaly.sensorDataId becomes NULL

// An Anomaly also belongs to a Sensor (redundant but useful for direct access)
Anomaly.belongsTo(Sensor, { foreignKey: 'sensorId', as: 'sensor' });
// A Sensor can have many Anomalies
Sensor.hasMany(Anomaly, { foreignKey: 'sensorId', as: 'anomalies' });


module.exports = Anomaly;