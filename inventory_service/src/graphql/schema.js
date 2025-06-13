const { gql } = require('apollo-server-express');

const typeDefs = gql`
  # Mendefinisikan tipe data untuk setiap item inventaris
  type Inventory {
    productId: String!
    warehouseId: String!
    stock: Int!
    updatedAt: String!
    warehouse: Warehouse
  }

  # Mendefinisikan tipe data untuk gudang
  type Warehouse {
    id: String!
    name: String!
    location: String
    inventory: [Inventory]
  }

  # Query yang tersedia untuk klien
  type Query {
    "Mendapatkan status inventaris untuk produk tertentu di semua gudang"
    getInventoryByProduct(productId: String!): [Inventory]

    "Mendapatkan status inventaris di gudang tertentu"
    getInventoryByWarehouse(warehouseId: String!): [Inventory]
    
    "Mendapatkan semua gudang"
    getAllWarehouses: [Warehouse]
  }

  # Input untuk mutasi update stok
  input UpdateStockInput {
    productId: String!
    warehouseId: String!
    quantityChange: Int! # Bisa positif (penambahan) atau negatif (pengurangan)
  }

  # Input untuk membuat gudang baru
  input CreateWarehouseInput {
    id: String!
    name: String!
    location: String
  }

  # Mutasi yang tersedia untuk mengubah data
  type Mutation {
    "Memperbarui stok untuk produk di gudang tertentu"
    updateStock(input: UpdateStockInput!): Inventory
    
    "Membuat gudang baru"
    createWarehouse(input: CreateWarehouseInput!): Warehouse
  }
`;

module.exports = typeDefs; 