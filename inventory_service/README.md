# Inventory Service

A GraphQL and REST API service for managing inventory data.

## Features

- Track product inventory across multiple warehouses
- GraphQL API for flexible data queries
- REST API for frontend integration
- SQLite database for easy setup

## Tech Stack

- Node.js
- Express
- Apollo Server
- Sequelize ORM
- SQLite

## Docker Setup

The inventory service can be run using Docker for easy setup and deployment.

### Prerequisites

- Docker
- Docker Compose

### Running with Docker

1. Build and run the container:

```bash
docker-compose up -d
```

2. Stop the container:

```bash
docker-compose down
```

## API Endpoints

### GraphQL

- GraphQL Endpoint: `http://localhost:4000/graphql`
- GraphQL Playground: `http://localhost:4000/graphql` (in browser)

### REST

- Get all warehouses: `GET http://localhost:4000/warehouses`
- Get inventory by product: `GET http://localhost:4000/inventory/product/:productId`
- Get inventory by warehouse: `GET http://localhost:4000/inventory/warehouse/:warehouseId`
- Update inventory: `POST http://localhost:4000/inventory/update`
- Create warehouse: `POST http://localhost:4000/warehouses`

## Development

### Local Setup

1. Install dependencies:

```bash
npm install
```

2. Run the service:

```bash
node src/index.js
```

The service will be available at http://localhost:4000.

## License

ISC 