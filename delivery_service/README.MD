# Delivery Service

A microservice built with Go for managing delivery details and statuses linked to orders in the EAI Bookstore system. This service provides endpoints for creating, retrieving, and updating delivery information.

## Tech Stack

- **Go (Golang)**: Primary programming language
- **PostgreSQL**: Database for storing delivery data
- **Gorilla Mux**: HTTP router for handling API requests
- **Docker**: Containerization

## Features

- **Delivery Creation**: Create new delivery records associated with an `order_id`.
- **Delivery Tracking**: Retrieve the status and details of a delivery using its `order_id`.
- **Status Updates**: Update the status of a delivery (e.g., `pending`, `preparing`, `on_the_way`, `delivered`, `cancelled`).
- **Database Integration**: Stores delivery information in a PostgreSQL database.
- **Health Check**: Endpoint to monitor service availability.

## API Endpoints

All endpoints assume the service is running on `http://localhost:5005` (or `http://delivery_service:5005` within Docker network).

### `POST /delivery/{order_id}` - Create a new delivery

Creates a delivery record for a given `order_id`.

-   **Path Parameters**:
    -   `order_id` (integer): The ID of the order for which to create a delivery.
-   **Request Body**:
    ```json
    {
        "order_id": 123,           // Should match the order_id in the URL
        "delivery_address": "123 Main St, Anytown, USA"
    }
    ```
-   **Responses**:
    -   `201 Created`: Delivery successfully created.
        ```json
        {
            "success": true,
            "message": "Delivery created successfully",
            "data": {
                "id": 1,
                "order_id": 123,
                "status": "pending",
                "estimated_time": "30-40 minutes",
                "delivery_address": "123 Main St, Anytown, USA",
                "created_at": "2024-06-17T10:00:00Z",
                "updated_at": "2024-06-17T10:00:00Z"
            }
        }
        ```
    -   `400 Bad Request`: Invalid input (e.g., missing address).
    -   `409 Conflict`: Delivery already exists for this order.
    -   `500 Internal Server Error`: Database error.

### `GET /delivery/{order_id}` - Get delivery details

Retrieves the delivery information for a specific `order_id`.

-   **Path Parameters**:
    -   `order_id` (integer): The ID of the order.
-   **Responses**:
    -   `200 OK`: Delivery details retrieved.
        ```json
        {
            "success": true,
            "message": "Delivery retrieved successfully",
            "data": {
                "id": 1,
                "order_id": 123,
                "status": "pending",
                "estimated_time": "30-40 minutes",
                "delivery_address": "123 Main St, Anytown, USA",
                "created_at": "2024-06-17T10:00:00Z",
                "updated_at": "2024-06-17T10:00:00Z"
            }
        }
        ```
    -   `404 Not Found`: Delivery not found for the given `order_id`.
    -   `500 Internal Server Error`: Database error.

### `PUT /delivery/{order_id}/status` - Update delivery status

Updates the status of a delivery for a given `order_id`.

-   **Path Parameters**:
    -   `order_id` (integer): The ID of the order.
-   **Request Body**:
    ```json
    {
        "status": "on_the_way" // Valid statuses: "pending", "preparing", "on_the_way", "delivered", "cancelled"
    }
    ```
-   **Responses**:
    -   `200 OK`: Status updated successfully.
    -   `400 Bad Request`: Invalid status value.
    -   `404 Not Found`: Delivery not found.
    -   `500 Internal Server Error`: Database error.

### `GET /health` - Health check

Checks the health of the delivery service and its database connection.

-   **Responses**:
    -   `200 OK`: Service is healthy.
        ```json
        {
            "status": "healthy",
            "service": "delivery-service",
            "timestamp": "2024-06-17T10:00:00Z",
            "database": "connected"
        }
        ```
    -   `200 OK` (with `unhealthy` status): Database disconnected.

## Installation & Running

### Using Docker (Recommended)

1.  **Ensure Docker and Docker Compose are installed.**
2.  **Navigate to the project root:** Your main `docker-compose.yml` should be in the parent directory of `delivery_service`.
3.  **Build and run the entire application**:
    ```bash
    docker-compose up --build
    ```
    This will build the `delivery_service` image using the `Dockerfile` and start all interconnected services.

### Local Development (without Docker)

1.  **Install Go**: Follow the official Go installation guide.
2.  **Install PostgreSQL**: Ensure you have a PostgreSQL server running and configured with a database named `delivery_db` and credentials matching those in `.env.example`.
3.  **Navigate to the `delivery_service` directory**:
    ```bash
    cd delivery_service
    ```
4.  **Set environment variables**:
    ```bash
    export DB_HOST=localhost
    export DB_PORT=5432 # Or your PostgreSQL port
    export DB_USER=postgres
    export DB_PASSWORD=password123
    export DB_NAME=delivery_db
    export PORT=8003 # Or your desired port, e.g., 5005
    ```
    (On Windows, use `set` instead of `export`).
5.  **Download Go modules**:
    ```bash
    go mod tidy
    ```
6.  **Run the application**:
    ```bash
    go run main.go
    ```

## Database Schema

The `delivery_service` uses the following database tables:

### `deliveries` Table
```sql
CREATE TABLE deliveries (
    id SERIAL PRIMARY KEY,
    order_id INTEGER UNIQUE NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    estimated_time VARCHAR(100),
    delivery_address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_deliveries_order_id ON deliveries(order_id);
CREATE INDEX idx_deliveries_status ON deliveries(status);