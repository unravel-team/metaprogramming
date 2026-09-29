// Package main serves the runnable Go scaffold application.
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"example.com/golang-scaffold/internal/mathx"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", healthHandler)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	server := &http.Server{
		Addr:              ":" + port,
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Printf("starting Go scaffold on :%s; mathx.Add(2, 3) = %d", port, mathx.Add(2, 3))
	log.Fatal(server.ListenAndServe())
}

// healthHandler responds to Fly health checks [tag:health-route].
func healthHandler(writer http.ResponseWriter, _ *http.Request) {
	writer.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(writer).Encode(map[string]string{"status": "ok"}); err != nil {
		log.Printf("write health response: %v", err)
	}
}
