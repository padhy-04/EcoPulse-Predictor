// backend/src/config/database.js
const { Sequelize } = require('sequelize');
require('dotenv').config(); // Load environment variables from .env file

/**
 * @file database.js
 * @description Configures and initializes the Sequelize database connection.
 * It uses environment variables for secure database credentials.
 */

// Retrieve database URL from environment variables
const DATABASE_URL = process.env.DATABASE_URL;

if (!DATABASE_URL) {
    console.error('Error: DATABASE_URL environment variable is not set.');
    // Exit the process if critical environment variable is missing
    process.exit(1);
}

// Initialize Sequelize with the database URL
const sequelize = new Sequelize(DATABASE_URL, {
    dialect: 'postgres', // Specify the database dialect (e.g., 'postgres', 'mysql', 'sqlite', 'mssql')
    logging: process.env.NODE_ENV === 'development' ? console.log : false, // Log SQL queries in development
    
    // Optional: dialectOptions for production-ready connections, e.g., with SSL
    dialectOptions: {
        // Example for PostgreSQL on services like Heroku, Render, Railway that require SSL
        ssl: process.env.NODE_ENV === 'production' ? {
            require: true,
            rejectUnauthorized: false // VERY IMPORTANT for self-signed certificates or specific cloud setups
        } : false, // No SSL in development unless specifically configured
    },
    
    // Connection pooling options (optional, can improve performance)
    pool: {
        max: 5,     // Maximum number of connection in pool
        min: 0,     // Minimum number of connection in pool
        acquire: 30000, // The maximum time, in ms, that pool will try to get connection before throwing error
        idle: 10000 // The maximum time, in ms, that a connection can be idle in the pool before being released
    },
});

/**
 * Function to authenticate the database connection.
 * This should be called once when the application starts.
 * It leverages the `sequelize.authenticate()` method.
 */
async function connectDB() {
    try {
        await sequelize.authenticate();
        console.log('Database connection has been established successfully.');
    } catch (error) {
        console.error('Unable to connect to the database:', error);
        // In a production environment, you might want more sophisticated error handling,
        // such as retries or custom alerts. For now, we'll exit the process.
        process.exit(1);
    }
}

// Export the sequelize instance and the connection function
module.exports = sequelize;
module.exports.connectDB = connectDB; // Export the function for external use (e.g., in server.js)