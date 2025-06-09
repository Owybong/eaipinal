package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
)

type Delivery struct {
	ID              int       `json:"id"`
	OrderID         int       `json:"order_id"`
	Status          string    `json:"status"`
	EstimatedTime   string    `json:"estimated_time"`
	DeliveryAddress string    `json:"delivery_address"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
}

type DeliveryRequest struct {
	OrderID         int    `json:"order_id"`
	DeliveryAddress string `json:"delivery_address"`
}

type DeliveryResponse struct {
	Success bool      `json:"success"`
	Message string    `json:"message"`
	Data    *Delivery `json:"data,omitempty"`
}

var db *sql.DB

func main() {
	// Initialize database connection
	initDB()
	defer db.Close()

	// Create tables
	createTables()

	// Setup routes
	router := mux.NewRouter()

	// Delivery endpoints
	router.HandleFunc("/delivery/{order_id}", createDelivery).Methods("POST")
	router.HandleFunc("/delivery/{order_id}", getDelivery).Methods("GET")
	router.HandleFunc("/delivery/{order_id}/status", updateDeliveryStatus).Methods("PUT")
	router.HandleFunc("/health", healthCheck).Methods("GET")

	// Add CORS middleware
	router.Use(corsMiddleware)

	port := getEnv("PORT", "8003")
	fmt.Printf("Delivery Service running on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, router))
}

func initDB() {
	host := getEnv("DB_HOST", "localhost")
	port := getEnv("DB_PORT", "5005")
	user := getEnv("DB_USER", "postgres")
	password := getEnv("DB_PASSWORD", "password123")
	dbname := getEnv("DB_NAME", "delivery_db")

	psqlInfo := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	var err error
	db, err = sql.Open("postgres", psqlInfo)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	err = db.Ping()
	if err != nil {
		log.Fatal("Failed to ping database:", err)
	}

	fmt.Println("Successfully connected to PostgreSQL database!")
}

func createTables() {
	query := `
	CREATE TABLE IF NOT EXISTS deliveries (
		id SERIAL PRIMARY KEY,
		order_id INTEGER UNIQUE NOT NULL,
		status VARCHAR(50) NOT NULL DEFAULT 'pending',
		estimated_time VARCHAR(100),
		delivery_address TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	);

	CREATE INDEX IF NOT EXISTS idx_deliveries_order_id ON deliveries(order_id);
	CREATE INDEX IF NOT EXISTS idx_deliveries_status ON deliveries(status);
	`

	_, err := db.Exec(query)
	if err != nil {
		log.Fatal("Failed to create tables:", err)
	}
	fmt.Println("Database tables created successfully!")
}

func createDelivery(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orderID, err := strconv.Atoi(vars["order_id"])
	if err != nil {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Invalid order ID",
		}, http.StatusBadRequest)
		return
	}

	var deliveryReq DeliveryRequest
	err = json.NewDecoder(r.Body).Decode(&deliveryReq)
	if err != nil {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Invalid request body",
		}, http.StatusBadRequest)
		return
	}

	// Validate required fields
	if deliveryReq.DeliveryAddress == "" {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Delivery address is required",
		}, http.StatusBadRequest)
		return
	}

	// Check if delivery already exists for this order
	var existingID int
	err = db.QueryRow("SELECT id FROM deliveries WHERE order_id = $1", orderID).Scan(&existingID)
	if err == nil {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Delivery already exists for this order",
		}, http.StatusConflict)
		return
	}

	// Generate estimated delivery time (30-60 minutes from now)
	estimatedMinutes := 30 + (orderID % 31) // Simple estimation based on order ID
	estimatedTimeStr := fmt.Sprintf("%d-%d minutes", estimatedMinutes, estimatedMinutes+10)

	// Create delivery record
	query := `
		INSERT INTO deliveries (order_id, status, estimated_time, delivery_address)
		VALUES ($1, $2, $3, $4)
		RETURNING id, created_at, updated_at
	`

	var delivery Delivery
	err = db.QueryRow(query, orderID, "pending", estimatedTimeStr, deliveryReq.DeliveryAddress).
		Scan(&delivery.ID, &delivery.CreatedAt, &delivery.UpdatedAt)
	if err != nil {
		log.Printf("Failed to create delivery: %v", err)
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Failed to create delivery",
		}, http.StatusInternalServerError)
		return
	}

	delivery.OrderID = orderID
	delivery.Status = "pending"
	delivery.EstimatedTime = estimatedTimeStr
	delivery.DeliveryAddress = deliveryReq.DeliveryAddress

	// Simulate communication with Order Service (in real implementation, make HTTP call)
	log.Printf("Would notify Order Service that delivery created for order %d", orderID)

	sendResponse(w, DeliveryResponse{
		Success: true,
		Message: "Delivery created successfully",
		Data:    &delivery,
	}, http.StatusCreated)
}

func getDelivery(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orderID, err := strconv.Atoi(vars["order_id"])
	if err != nil {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Invalid order ID",
		}, http.StatusBadRequest)
		return
	}

	var delivery Delivery
	query := `
		SELECT id, order_id, status, estimated_time, delivery_address, created_at, updated_at
		FROM deliveries
		WHERE order_id = $1
	`

	err = db.QueryRow(query, orderID).Scan(
		&delivery.ID,
		&delivery.OrderID,
		&delivery.Status,
		&delivery.EstimatedTime,
		&delivery.DeliveryAddress,
		&delivery.CreatedAt,
		&delivery.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Delivery not found for this order",
		}, http.StatusNotFound)
		return
	}

	if err != nil {
		log.Printf("Failed to get delivery: %v", err)
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Failed to retrieve delivery",
		}, http.StatusInternalServerError)
		return
	}

	sendResponse(w, DeliveryResponse{
		Success: true,
		Message: "Delivery retrieved successfully",
		Data:    &delivery,
	}, http.StatusOK)
}

func updateDeliveryStatus(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orderID, err := strconv.Atoi(vars["order_id"])
	if err != nil {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Invalid order ID",
		}, http.StatusBadRequest)
		return
	}

	var statusUpdate struct {
		Status string `json:"status"`
	}

	err = json.NewDecoder(r.Body).Decode(&statusUpdate)
	if err != nil {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Invalid request body",
		}, http.StatusBadRequest)
		return
	}

	// Validate status
	validStatuses := map[string]bool{
		"pending":    true,
		"preparing":  true,
		"on_the_way": true,
		"delivered":  true,
		"cancelled":  true,
	}

	if !validStatuses[statusUpdate.Status] {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Invalid status. Valid statuses: pending, preparing, on_the_way, delivered, cancelled",
		}, http.StatusBadRequest)
		return
	}

	// Update delivery status
	query := `
		UPDATE deliveries 
		SET status = $1, updated_at = CURRENT_TIMESTAMP
		WHERE order_id = $2
		RETURNING id, order_id, status, estimated_time, delivery_address, created_at, updated_at
	`

	var delivery Delivery
	err = db.QueryRow(query, statusUpdate.Status, orderID).Scan(
		&delivery.ID,
		&delivery.OrderID,
		&delivery.Status,
		&delivery.EstimatedTime,
		&delivery.DeliveryAddress,
		&delivery.CreatedAt,
		&delivery.UpdatedAt,
	)

	if err == sql.ErrNoRows {
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Delivery not found for this order",
		}, http.StatusNotFound)
		return
	}

	if err != nil {
		log.Printf("Failed to update delivery status: %v", err)
		sendResponse(w, DeliveryResponse{
			Success: false,
			Message: "Failed to update delivery status",
		}, http.StatusInternalServerError)
		return
	}

	sendResponse(w, DeliveryResponse{
		Success: true,
		Message: "Delivery status updated successfully",
		Data:    &delivery,
	}, http.StatusOK)
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	response := map[string]interface{}{
		"status":    "healthy",
		"service":   "delivery-service",
		"timestamp": time.Now().Format(time.RFC3339),
		"database":  "connected",
	}

	// Test database connection
	err := db.Ping()
	if err != nil {
		response["database"] = "disconnected"
		response["status"] = "unhealthy"
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func corsMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if r.Method == "OPTIONS" {
			w.WriteHeader(http.StatusOK)
			return
		}

		next.ServeHTTP(w, r)
	})
}

func sendResponse(w http.ResponseWriter, response DeliveryResponse, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(response)
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}
