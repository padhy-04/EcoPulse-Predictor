// backend/src/models/index.js
const sequelize = require('../config/database'); // Adjust path if needed
const Sensor = require('./sensor');
const SensorData = require('./sensorData');
const Anomaly = require('./anomaly');

const db = {};

db.sequelize = sequelize;
db.Sequelize = sequelize.Sequelize; // Make Sequelize library available if needed

// Add models to the db object
db.Sensor = Sensor;
db.SensorData = SensorData;
db.Anomaly = Anomaly;

// Define any additional global associations here if not already defined in model files
// For example:
// db.Sensor.hasMany(db.SensorData, { foreignKey: 'sensorId', as: 'data' });
// db.SensorData.belongsTo(db.Sensor, { foreignKey: 'sensorId', as: 'sensor' });
// db.SensorData.hasOne(db.Anomaly, { foreignKey: 'sensorDataId', as: 'anomaly', onDelete: 'SET NULL' });
// db.Anomaly.belongsTo(db.SensorData, { foreignKey: 'sensorDataId', as: 'sensor_data' });
// db.Sensor.hasMany(db.Anomaly, { foreignKey: 'sensorId', as: 'anomalies' });
// db.Anomaly.belongsTo(db.Sensor, { foreignKey: 'sensorId', as: 'sensor' });


// This function will connect to the DB and sync models (create tables)
db.syncModels = async () => {
    try {
        await sequelize.authenticate();
        console.log('Database connection has been established successfully.');
        // `alter: true` is good for development to update schemas without dropping data
        // For production, consider using Sequelize migrations
        await sequelize.sync({ alter: true });
        console.log("All models were synchronized successfully.");
    } catch (error) {
        console.error('Unable to connect to the database or sync models:', error);
        // In production, you might want to gracefully exit or retry
        process.exit(1);
    }
};

module.exports = db;