const sequelize = require('./index');
const { Warehouse, Inventory } = require('../models');

// Function to initialize the database
async function initDatabase() {
  try {
    // Sync all models with the database
    await sequelize.sync({ force: true });
    console.log('Database synchronized successfully');

    // Create some initial warehouses
    const warehouses = await Warehouse.bulkCreate([
      { id: 'WH001', name: 'Main Warehouse', location: 'Jakarta' },
      { id: 'WH002', name: 'East Warehouse', location: 'Surabaya' },
      { id: 'WH003', name: 'West Warehouse', location: 'Bandung' }
    ]);
    console.log(`${warehouses.length} warehouses created`);

    // Create some initial inventory items
    const inventoryItems = await Inventory.bulkCreate([
      { productId: 'P001', warehouseId: 'WH001', stock: 100 },
      { productId: 'P002', warehouseId: 'WH001', stock: 50 },
      { productId: 'P001', warehouseId: 'WH002', stock: 75 },
      { productId: 'P003', warehouseId: 'WH003', stock: 200 }
    ]);
    console.log(`${inventoryItems.length} inventory items created`);

    console.log('Database initialization completed successfully');
  } catch (error) {
    console.error('Error initializing database:', error);
  }
}

// If this file is run directly, initialize the database
if (require.main === module) {
  initDatabase()
    .then(() => {
      console.log('Database initialization script completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Database initialization script failed:', error);
      process.exit(1);
    });
}

module.exports = initDatabase; 