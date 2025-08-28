// backend/src/server.js
const app = require('./app');
const db = require('./models'); // This imports the db object from models/index.js
require('dotenv').config();

const PORT = process.env.PORT || 3000;

async function startServer() {
    // The db.syncModels() function (from models/index.js) already calls sequelize.authenticate()
    // and then performs database synchronization. So, calling connectDB explicitly here
    // might be redundant depending on how db.syncModels() is implemented.
    // If db.syncModels() only syncs models, then you'd also call connectDB().
    // Assuming db.syncModels() also authenticates:
    await db.syncModels(); 

    app.listen(PORT, () => {
        console.log(`Backend server running on port ${PORT}`);
        console.log(`ML Service URL: ${process.env.ML_SERVICE_URL}`);
        console.log(`Database connected successfully and models synchronized.`);
    });
}

startServer();