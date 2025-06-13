const { DataTypes } = require('sequelize');
const sequelize = require('../database');
const Warehouse = require('./Warehouse');

const Inventory = sequelize.define('Inventory', {
  productId: {
    type: DataTypes.STRING,
    primaryKey: true,
    allowNull: false,
    field: 'product_id'
  },
  warehouseId: {
    type: DataTypes.STRING,
    primaryKey: true,
    allowNull: false,
    field: 'warehouse_id',
    references: {
      model: Warehouse,
      key: 'id'
    }
  },
  stock: {
    type: DataTypes.INTEGER,
    allowNull: false,
    defaultValue: 0
  },
  updatedAt: {
    type: DataTypes.DATE,
    field: 'updated_at'
  }
}, {
  tableName: 'inventory',
  timestamps: true,
  createdAt: false
});

// Define relationship
Inventory.belongsTo(Warehouse, { foreignKey: 'warehouseId' });
Warehouse.hasMany(Inventory, { foreignKey: 'warehouseId' });

module.exports = Inventory; 