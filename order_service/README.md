# Order Service

A microservice for managing orders in the EAI Bookstore system. This service handles order creation, management, and tracking.

## Features

- Create new orders with multiple items
- Retrieve order details
- Update order status
- Delete orders
- Automatic product price validation
- Customer validation
- Fallback to JSON storage when MySQL is unavailable

## Tech Stack

- Python 3.10
- Flask
- MySQL (primary storage)
- JSON (fallback storage)
- Docker

## API Endpoints

### GET /orders
Retrieve all orders

**Response**
```json
[
    {
        "id": 1,
        "customer_id": 1,
        "created_at": "2024-03-20T10:00:00",
        "updated_at": "2024-03-20T10:00:00",
        "status": "COMPLETED",
        "total_amount": 59.97,
        "items": [
            {
                "id": 1,
                "product_id": 1,
                "quantity": 3,
                "unit_price": 19.99
            }
        ]
    }
]
```

### GET /orders/{order_id}
Retrieve a specific order

**Response**
```json
{
    "id": 1,
    "customer_id": 1,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00",
    "status": "COMPLETED",
    "total_amount": 59.97,
    "items": [
        {
            "id": 1,
            "product_id": 1,
            "quantity": 3,
            "unit_price": 19.99
        }
    ]
}
```

### POST /orders
Create a new order

**Request Body**
```json
{
    "customer_id": 1,
    "items": [
        {
            "product_id": 1,
            "quantity": 3
        }
    ]
}
```

**Response**
```json
{
    "id": 1,
    "customer_id": 1,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00",
    "status": "PENDING",
    "total_amount": 59.97,
    "items": [
        {
            "id": 1,
            "product_id": 1,
            "quantity": 3,
            "unit_price": 19.99
        }
    ]
}
```

### PUT /orders/{order_id}
Update order status

**Request Body**
```json
{
    "status": "COMPLETED"
}
```

**Response**
```json
{
    "id": 1,
    "customer_id": 1,
    "created_at": "2024-03-20T10:00:00",
    "updated_at": "2024-03-20T10:00:00",
    "status": "COMPLETED",
    "total_amount": 59.97,
    "items": [
        {
            "id": 1,
            "product_id": 1,
            "quantity": 3,
            "unit_price": 19.99
        }
    ]
}
```

### DELETE /orders/{order_id}
Delete an order

**Response**
```json
{
    "message": "Order deleted successfully"
}
```

## Order Status Values

- `PENDING`: Initial state when order is created
- `PROCESSING`: Order is being processed
- `COMPLETED`: Order has been fulfilled
- `CANCELLED`: Order was cancelled

## Installation & Running

### Using Docker (Recommended)

1. Pull the image:
```bash
docker pull comiscs/tubes_eai:order_service
```

2. Create a docker-compose.yml:
```yaml
version: '3.8'

services:
  order-service:
    image: comiscs/tubes_eai:order_service
    ports:
      - "5004:5004"
    environment:
      - MYSQL_HOST=mysql
      - MYSQL_PORT=3306
      - MYSQL_USER=root
      - MYSQL_PASSWORD=
      - MYSQL_DATABASE=order_db
    volumes:
      - ./data:/app/data
    depends_on:
      - mysql
    networks:
      - bookstore-network

  mysql:
    image: mysql:8.0
    ports:
      - "3308:3306"
    environment:
      - MYSQL_ALLOW_EMPTY_PASSWORD=yes
      - MYSQL_DATABASE=order_db
    volumes:
      - mysql-data:/var/lib/mysql
    networks:
      - bookstore-network

volumes:
  mysql-data:

networks:
  bookstore-network:
    name: bookstore-network
```

3. Run the service:
```bash
docker-compose up
```

### Manual Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL database
4. Run the service:
```bash
python app.py
```

## Environment Variables

- `MYSQL_HOST`: MySQL host (default: localhost)
- `MYSQL_PORT`: MySQL port (default: 3308)
- `MYSQL_USER`: MySQL user (default: root)
- `MYSQL_PASSWORD`: MySQL password (default: empty)
- `MYSQL_DATABASE`: MySQL database name (default: order_db)

## Storage Modes

The service supports two storage modes:

1. **MySQL Storage** (Primary)
   - Used when MySQL connection is available
   - Provides full ACID compliance
   - Better for production use

2. **JSON Storage** (Fallback)
   - Used when MySQL connection fails
   - Data stored in `data/orders.json`
   - Suitable for development/testing

## Integration Points

The service integrates with:

1. **Customer Service** (port 5000)
   - Validates customer existence during order creation
   - Uses GraphQL API

2. **Product Service** (port 5002)
   - Validates product existence
   - Fetches current product prices
   - Uses REST API

## Error Handling

The service returns appropriate HTTP status codes:

- 200: Successful operation
- 201: Resource created
- 400: Bad request (invalid input)
- 404: Resource not found
- 503: Service unavailable (integration service down)

## Development

### Building the Docker Image

```bash
docker build -t order_service .
docker tag order_service comiscs/tubes_eai:order_service
docker push comiscs/tubes_eai:order_service
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 