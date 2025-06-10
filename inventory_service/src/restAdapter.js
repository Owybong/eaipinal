const express = require('express');
const { Inventory, Warehouse } = require('./models');
const { ApolloClient, InMemoryCache, gql } = require('@apollo/client/core');
const fetch = require('cross-fetch');

// Create a GraphQL client to interact with our own GraphQL API
const client = new ApolloClient({
  uri: 'http://inventory_service:5003/graphql',
  cache: new InMemoryCache(),
  fetch
});

// Create a router for inventory REST endpoints
const router = express.Router();

// GET all warehouses
router.get('/warehouses', async (req, res) => {
  try {
    const { data } = await client.query({
      query: gql`
        query GetAllWarehouses {
          getAllWarehouses {
            id
            name
            location
          }
        }
      `
    });
    
    res.json(data.getAllWarehouses);
  } catch (error) {
    console.error('Error fetching warehouses:', error);
    res.status(500).json({ error: 'Failed to fetch warehouses' });
  }
});

// GET inventory by product ID
router.get('/inventory/product/:productId', async (req, res) => {
  try {
    const { productId } = req.params;
    
    const { data } = await client.query({
      query: gql`
        query GetInventoryByProduct($productId: String!) {
          getInventoryByProduct(productId: $productId) {
            productId
            warehouseId
            stock
            updatedAt
            warehouse {
              id
              name
              location
            }
          }
        }
      `,
      variables: { productId }
    });
    
    res.json(data.getInventoryByProduct);
  } catch (error) {
    console.error('Error fetching inventory by product:', error);
    res.status(500).json({ error: 'Failed to fetch inventory' });
  }
});

// GET inventory by warehouse ID
router.get('/inventory/warehouse/:warehouseId', async (req, res) => {
  try {
    const { warehouseId } = req.params;
    
    const { data } = await client.query({
      query: gql`
        query GetInventoryByWarehouse($warehouseId: String!) {
          getInventoryByWarehouse(warehouseId: $warehouseId) {
            productId
            warehouseId
            stock
            updatedAt
            warehouse {
              id
              name
              location
            }
          }
        }
      `,
      variables: { warehouseId }
    });
    
    res.json(data.getInventoryByWarehouse);
  } catch (error) {
    console.error('Error fetching inventory by warehouse:', error);
    res.status(500).json({ error: 'Failed to fetch inventory' });
  }
});

// POST update inventory stock
router.post('/inventory/update', async (req, res) => {
  try {
    const { productId, warehouseId, quantityChange } = req.body;
    
    const { data } = await client.mutate({
      mutation: gql`
        mutation UpdateStock($input: UpdateStockInput!) {
          updateStock(input: $input) {
            productId
            warehouseId
            stock
            updatedAt
          }
        }
      `,
      variables: {
        input: {
          productId,
          warehouseId,
          quantityChange: parseInt(quantityChange, 10)
        }
      }
    });
    
    res.json(data.updateStock);
  } catch (error) {
    console.error('Error updating stock:', error);
    res.status(500).json({ error: 'Failed to update stock' });
  }
});

// POST create new warehouse
router.post('/warehouses', async (req, res) => {
  try {
    const { id, name, location } = req.body;
    
    const { data } = await client.mutate({
      mutation: gql`
        mutation CreateWarehouse($input: CreateWarehouseInput!) {
          createWarehouse(input: $input) {
            id
            name
            location
          }
        }
      `,
      variables: {
        input: {
          id,
          name,
          location: location || ""
        }
      }
    });
    
    res.status(201).json(data.createWarehouse);
  } catch (error) {
    console.error('Error creating warehouse:', error);
    res.status(500).json({ error: 'Failed to create warehouse' });
  }
});

module.exports = router; 