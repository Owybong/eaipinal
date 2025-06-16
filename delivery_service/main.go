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
	_ "github.com/lib/pq" // PostgreSQL driver
)

// Delivery represents the structure of a delivery record
type Delivery struct {
	ID              int       `json:"id"`
	OrderID         int       `json:"order_id"`
	Status          string    `json:"status"`
	EstimatedTime   string    `json:"estimated_time"`
	DeliveryAddress string    `json:"delivery_address"`
	CreatedAt       time.Time `json:"created_at"`
	UpdatedAt       time.Time `json:"updated_at"`
}

// Global variable for database connection
var db *sql.DB

// Helper to get environment variables with default values
func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}

func main() {
	// Initialize database connection
	dbHost := getEnv("DB_HOST", "postgres_db") // Use Docker Compose service name
	dbPort := getEnv("DB_PORT", "5432")
	dbUser := getEnv("DB_USER", "user")
	dbPassword := getEnv("DB_PASSWORD", "password")
	dbName := getEnv("DB_NAME", "inventory_db") // Assuming same DB as inventory, adjust if new DB for delivery

	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)

	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Error opening database connection: %v", err)
	}
	defer db.Close()

	// Ping the database to ensure connection is established
	err = db.Ping()
	if err != nil {
		log.Fatalf("Error connecting to the database: %v", err)
	}
	log.Println("Successfully connected to the database!")

	// Initialize the router
	router := mux.NewRouter()

	// --- API Endpoints ---
	router.HandleFunc("/health", healthCheckHandler).Methods("GET")
	router.HandleFunc("/delivery/{order_id}", createDeliveryHandler).Methods("POST")
	router.HandleFunc("/delivery/{order_id}", getDeliveryHandler).Methods("GET")
	router.HandleFunc("/delivery/{order_id}/status", updateDeliveryStatusHandler).Methods("PUT")

	// Start the HTTP server
	port := getEnv("PORT", "5005") // Match with docker-compose.yml exposed port
	log.Printf("Delivery Service starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, router))
}

// Handler for health check endpoint
func healthCheckHandler(w http.ResponseWriter, r *http.Request) {
	status := "healthy"
	dbStatus := "connected"
	if err := db.Ping(); err != nil {
		status = "unhealthy" // Service is unhealthy if DB is down for this check
		dbStatus = "disconnected"
		log.Printf("Health check: Database disconnected - %v", err)
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"status":    status,
		"service":   "delivery-service",
		"timestamp": time.Now().Format(time.RFC3339),
		"database":  dbStatus,
	})
}

// Handler to create a new delivery record
func createDeliveryHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orderIDStr := vars["order_id"]
	orderID, err := strconv.Atoi(orderIDStr)
	if err != nil {
		http.Error(w, `{"success": false, "message": "Invalid Order ID"}`, http.StatusBadRequest)
		return
	}

	var reqBody struct {
		DeliveryAddress string `json:"delivery_address"`
	}
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		http.Error(w, `{"success": false, "message": "Invalid request body"}`, http.StatusBadRequest)
		return
	}

	if reqBody.DeliveryAddress == "" {
		http.Error(w, `{"success": false, "message": "Delivery address cannot be empty"}`, http.StatusBadRequest)
		return
	}

	// Check if a delivery for this order_id already exists
	var existingID int
	err = db.QueryRow("SELECT id FROM deliveries WHERE order_id = $1", orderID).Scan(&existingID)
	if err == nil {
		http.Error(w, `{"success": false, "message": "Delivery already exists for this order ID"}`, http.StatusConflict)
		return
	}
	if err != sql.ErrNoRows {
		log.Printf("Database error checking existing delivery: %v", err)
		http.Error(w, `{"success": false, "message": "Database error"}`, http.StatusInternalServerError)
		return
	}

	var newDelivery Delivery
	newDelivery.OrderID = orderID
	newDelivery.DeliveryAddress = reqBody.DeliveryAddress
	newDelivery.Status = "pending" // Default status
	newDelivery.EstimatedTime = "30-40 minutes" // Example default

	query := `INSERT INTO deliveries (order_id, status, estimated_time, delivery_address)
              VALUES ($1, $2, $3, $4) RETURNING id, created_at, updated_at`

	err = db.QueryRow(query, newDelivery.OrderID, newDelivery.Status,
		newDelivery.EstimatedTime, newDelivery.DeliveryAddress).Scan(
		&newDelivery.ID, &newDelivery.CreatedAt, &newDelivery.UpdatedAt)

	if err != nil {
		log.Printf("Error inserting new delivery: %v", err)
		http.Error(w, `{"success": false, "message": "Failed to create delivery"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "Delivery created successfully",
		"data":    newDelivery,
	})
}

// Handler to get delivery details by order ID
func getDeliveryHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orderIDStr := vars["order_id"]
	orderID, err := strconv.Atoi(orderIDStr)
	if err != nil {
		http.Error(w, `{"success": false, "message": "Invalid Order ID"}`, http.StatusBadRequest)
		return
	}

	var delivery Delivery
	query := `SELECT id, order_id, status, estimated_time, delivery_address, created_at, updated_at
              FROM deliveries WHERE order_id = $1`
	row := db.QueryRow(query, orderID)
	err = row.Scan(&delivery.ID, &delivery.OrderID, &delivery.Status, &delivery.EstimatedTime,
		&delivery.DeliveryAddress, &delivery.CreatedAt, &delivery.UpdatedAt)

	if err == sql.ErrNoRows {
		http.Error(w, `{"success": false, "message": "Delivery not found"}`, http.StatusNotFound)
		return
	}
	if err != nil {
		log.Printf("Error fetching delivery: %v", err)
		http.Error(w, `{"success": false, "message": "Database error"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "Delivery retrieved successfully",
		"data":    delivery,
	})
}

// Handler to update delivery status by order ID
func updateDeliveryStatusHandler(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	orderIDStr := vars["order_id"]
	orderID, err := strconv.Atoi(orderIDStr)
	if err != nil {
		http.Error(w, `{"success": false, "message": "Invalid Order ID"}`, http.StatusBadRequest)
		return
	}

	var reqBody struct {
		Status string `json:"status"`
	}
	if err := json.NewDecoder(r.Body).Decode(&reqBody); err != nil {
		http.Error(w, `{"success": false, "message": "Invalid request body"}`, http.StatusBadRequest)
		return
	}

	// Validate status
	validStatuses := map[string]bool{
		"pending":      true,
		"preparing":    true,
		"on_the_way":   true,
		"delivered":    true,
		"cancelled":    true,
	}
	if !validStatuses[reqBody.Status] {
		http.Error(w, `{"success": false, "message": "Invalid status value"}`, http.StatusBadRequest)
		return
	}

	result, err := db.Exec(`UPDATE deliveries SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE order_id = $2`,
		reqBody.Status, orderID)
	if err != nil {
		log.Printf("Error updating delivery status: %v", err)
		http.Error(w, `{"success": false, "message": "Failed to update delivery status"}`, http.StatusInternalServerError)
		return
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil || rowsAffected == 0 {
		http.Error(w, `{"success": false, "message": "Delivery not found or no changes made"}`, http.StatusNotFound)
		return
	}

	// Optionally, fetch the updated delivery to return
	var updatedDelivery Delivery
	query := `SELECT id, order_id, status, estimated_time, delivery_address, created_at, updated_at
              FROM deliveries WHERE order_id = $1`
	row := db.QueryRow(query, orderID)
	err = row.Scan(&updatedDelivery.ID, &updatedDelivery.OrderID, &updatedDelivery.Status, &updatedDelivery.EstimatedTime,
		&updatedDelivery.DeliveryAddress, &updatedDelivery.CreatedAt, &updatedDelivery.UpdatedAt)

	if err != nil {
		log.Printf("Error fetching updated delivery: %v", err)
		http.Error(w, `{"success": false, "message": "Successfully updated status, but failed to retrieve updated details"}`, http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"success": true,
		"message": "Delivery status updated successfully",
		"data":    updatedDelivery,
	})
}
