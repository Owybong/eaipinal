const { DataTypes } = require('sequelize');
const sequelize = require('../database');

const Warehouse = sequelize.define('Warehouse', {
  id: {
    type: DataTypes.STRING,
    primaryKey: true,
    allowNull: false
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  location: {
    type: DataTypes.TEXT,
    allowNull: true
  }
}, {
  tableName: 'warehouses',
  timestamps: true
});

module.exports = Warehouse; 