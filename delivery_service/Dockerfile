# Dockerfile for Go Delivery Service

# --- Builder Stage ---
# Use an official Go image that meets the 1.24.4 requirement or later
FROM golang:1.24.4-alpine AS builder

# Set necessary environment variables for CGO_ENABLED (important for PostgreSQL driver)
ENV CGO_ENABLED=1

# Install Git, build dependencies, and bash for wait-for-it.sh
RUN apk add --no-cache git gcc musl-dev bash

# Set the working directory inside the container
WORKDIR /app

# Copy go.mod and go.sum files to download dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the application source code (including main.go)
COPY . .

# Build the Go application binary
# CGO_ENABLED=1 is crucial for the pq (PostgreSQL) driver
RUN go build -o /delivery_service ./main.go

# --- Runner Stage ---
# Use a minimal Alpine Linux image for the final runtime
FROM alpine:latest

# Install curl for health checks and bash for wait-for-it.sh
RUN apk add --no-cache curl bash

# Install wait-for-it.sh script
RUN wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Set the working directory
WORKDIR /app

# Copy the built Go binary from the builder stage
COPY --from=builder /delivery_service .

# Copy the .env.example as a reference (not directly used by app, but good for context)
COPY .env.example .

# Expose the port the application listens on.
# Based on your docker-compose.yml, it's mapped to 5005.
EXPOSE 5005

# Command to run the application, waiting for the PostgreSQL database (postgres_db service)
# It waits for postgres_db on port 5432 for up to 60 seconds.
CMD ["sh", "-c", "wait-for-it.sh postgres_db:5432 -t 60 -- /app/delivery_service"]
