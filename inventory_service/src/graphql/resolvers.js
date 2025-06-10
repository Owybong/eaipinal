const { Inventory, Warehouse } = require('../models');
const sequelize = require('../database');

const resolvers = {
  Query: {
    getInventoryByProduct: async (_, { productId }) => {
      return await Inventory.findAll({
        where: { productId },
        include: [Warehouse]
      });
    },
    getInventoryByWarehouse: async (_, { warehouseId }) => {
      return await Inventory.findAll({
        where: { warehouseId },
        include: [Warehouse]
      });
    },
    getAllWarehouses: async () => {
      return await Warehouse.findAll();
    }
  },
  Mutation: {
    updateStock: async (_, { input }) => {
      const { productId, warehouseId, quantityChange } = input;
      
      // Start a transaction to ensure data consistency
      const t = await sequelize.transaction();
      
      try {
        // Find the current inventory record
        let inventory = await Inventory.findOne({
          where: { productId, warehouseId },
          transaction: t
        });
        
        if (!inventory) {
          // If inventory record doesn't exist, create it
          inventory = await Inventory.create({
            productId,
            warehouseId,
            stock: 0
          }, { transaction: t });
        }
        
        // Calculate new stock value
        const newStock = inventory.stock + quantityChange;
        
        // Check if the new stock would be negative
        if (newStock < 0) {
          throw new Error('Cannot reduce stock below zero');
        }
        
        // Update the stock
        await inventory.update({ 
          stock: newStock,
          updatedAt: new Date()
        }, { transaction: t });
        
        // Commit the transaction
        await t.commit();
        
        // Return the updated inventory
        return await Inventory.findOne({
          where: { productId, warehouseId },
          include: [Warehouse]
        });
      } catch (error) {
        // Rollback the transaction in case of error
        await t.rollback();
        throw error;
      }
    },
    createWarehouse: async (_, { input }) => {
      const { id, name, location } = input;
      
      try {
        // Check if warehouse with the ID already exists
        const existingWarehouse = await Warehouse.findByPk(id);
        if (existingWarehouse) {
          throw new Error(`Warehouse with ID ${id} already exists`);
        }
        
        // Create new warehouse
        return await Warehouse.create({
          id,
          name,
          location
        });
      } catch (error) {
        throw error;
      }
    }
  },
  // Field resolvers for type definitions
  Inventory: {
    warehouse: async (parent) => {
      return await Warehouse.findByPk(parent.warehouseId);
    }
  },
  Warehouse: {
    inventory: async (parent) => {
      return await Inventory.findAll({
        where: { warehouseId: parent.id }
      });
    }
  }
};

module.exports = resolvers; 