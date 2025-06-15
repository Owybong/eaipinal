# Inventory Service - Python GraphQL API

A modern GraphQL API for inventory and warehouse management built with Python, FastAPI, and Strawberry GraphQL.

## Tech Stack

- **Python 3.11**
- **FastAPI** - Modern, fast web framework
- **Strawberry GraphQL** - Modern GraphQL library for Python
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Primary database
- **Databases** - Async database interface
- **Uvicorn** - ASGI server
- **Docker** - Containerization

## Features

- **GraphQL API** with full introspection and playground
- **REST API** for backward compatibility
- **Async/await** support for high performance
- **Database transactions** for data consistency
- **Health checks** and monitoring
- **CORS** enabled for cross-origin requests
- **Docker** containerization

## API Endpoints

### GraphQL

- **GraphQL Endpoint**: `http://localhost:5003/graphql`
- **GraphQL Playground**: `http://localhost:5003/graphql` (in browser)

### REST (Backward Compatibility)

- `GET /warehouses` - Get all warehouses
- `GET /inventory/product/{product_id}` - Get inventory by product
- `GET /inventory/warehouse/{warehouse_id}` - Get inventory by warehouse
- `POST /inventory/update` - Update inventory stock
- `POST /warehouses` - Create new warehouse

### Health & Info

- `GET /` - API information
- `GET /health` - Health check

## GraphQL Schema

### Types

```graphql
type Warehouse {
  id: String!
  name: String!
  location: String
  createdAt: DateTime!
  updatedAt: DateTime!
  inventory: [Inventory!]!
}

type Inventory {
  productId: String!
  warehouseId: String!
  stock: Int!
  updatedAt: DateTime!
  warehouse: Warehouse
}
```

### Queries

```graphql
type Query {
  getAllWarehouses: [Warehouse!]!
  getInventoryByProduct(productId: String!): [Inventory!]!
  getInventoryByWarehouse(warehouseId: String!): [Inventory!]!
}
```

### Mutations

```graphql
type Mutation {
  createWarehouse(input: CreateWarehouseInput!): Warehouse!
  updateStock(input: UpdateStockInput!): Inventory!
}

input CreateWarehouseInput {
  id: String!
  name: String!
  location: String
}

input UpdateStockInput {
  productId: String!
  warehouseId: String!
  quantityChange: Int!
}
```

## Installation & Running

### Using Docker (Recommended)

1. **Build and run with docker-compose** (from project root):
   ```bash
   docker-compose up inventory_service
   ```

2. **Or build manually**:
   ```bash
   cd inventory_service
   docker build -t inventory-service .
   docker run -p 5003:5003 \
     -e DATABASE_URL=postgresql://user:password@postgres_db:5432/inventory_db \
     inventory-service
   ```

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database configuration
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

## Database Schema

### Warehouses Table
```sql
CREATE TABLE warehouses (
    id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Inventory Table
```sql
CREATE TABLE inventory (
    product_id VARCHAR NOT NULL,
    warehouse_id VARCHAR NOT NULL REFERENCES warehouses(id),
    stock INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (product_id, warehouse_id)
);
```

## Example Usage

### GraphQL Queries

**Get all warehouses:**
```graphql
query {
  getAllWarehouses {
    id
    name
    location
    inventory {
      productId
      stock
    }
  }
}
```

**Get inventory for a product:**
```graphql
query {
  getInventoryByProduct(productId: "PROD001") {
    warehouseId
    stock
    warehouse {
      name
      location
    }
  }
}
```

**Update stock:**
```graphql
mutation {
  updateStock(input: {
    productId: "PROD001"
    warehouseId: "WH001"
    quantityChange: 10
  }) {
    productId
    warehouseId
    stock
    updatedAt
  }
}
```

### REST API Examples

**Get all warehouses:**
```bash
curl http://localhost:5003/warehouses
```

**Update stock:**
```bash
curl -X POST http://localhost:5003/inventory/update \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "PROD001",
    "warehouse_id": "WH001",
    "quantity_change": 10
  }'
```

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `PORT` - Server port (default: 5003)
- `NODE_ENV` - Environment (development/production)

## Migration from Node.js

This service replaces the previous Node.js implementation with the following improvements:

- **Better Performance**: Async/await with FastAPI
- **Type Safety**: Full type hints and Pydantic models
- **Modern GraphQL**: Strawberry GraphQL with automatic schema generation
- **Better Error Handling**: Structured error responses
- **Health Monitoring**: Built-in health checks
- **Backward Compatibility**: REST endpoints maintained

## Development

### Code Structure
```
inventory_service/
├── app.py              # Main FastAPI application
├── database.py         # Database configuration
├── models.py           # SQLAlchemy models
├── schema.py           # GraphQL schema and resolvers
├── rest_adapter.py     # REST API endpoints
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md          # This file
```

### Adding New Features

1. **Add new models** in `models.py`
2. **Add GraphQL types** in `schema.py`
3. **Add REST endpoints** in `rest_adapter.py` (if needed)
4. **Update database schema** as needed

## Monitoring

- Health check endpoint: `GET /health`
- Docker health check included
- Structured logging with timestamps
- Database connection monitoring