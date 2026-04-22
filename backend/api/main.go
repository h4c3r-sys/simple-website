package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

type Server struct {
	ID   string `json:"id"`
	Name string `json:"name"`
}

type Channel struct {
	ID       string `json:"id"`
	ServerID string `json:"server_id"`
	Name     string `json:"name"`
}

func main() {
	http.HandleFunc("/api/health", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Go API is healthy"))
	})

	http.HandleFunc("/api/servers", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			// Mock response for now, in a real scenario this queries ScyllaDB
			servers := []Server{{ID: "1", Name: "General Server"}}
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(servers)
		} else if r.Method == "POST" {
			// Handle Server Creation
			w.WriteHeader(http.StatusCreated)
		}
	})

    http.HandleFunc("/api/channels", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "GET" {
			// Mock response
			channels := []Channel{{ID: "1", ServerID: "1", Name: "general"}}
			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(channels)
		}
	})

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	fmt.Printf("Go API starting on port %s\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
