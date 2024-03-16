package main

import (
	"encoding/json"
	"fmt"
	"github.com/gorilla/mux"
	"net/http"
	"os"
	"strings"
)

func getEnv(key, fallback string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return fallback
}

var koboldAPIURL = getEnv("KOBOLD_API_URL", "https://api.aipowergrid.io/api/v2/generate/text/async")
var koboldStatusURL = "https://horde.koboldai.net/api/v2/generate/text/status/"
var defaultAPIKey = getEnv("DEFAULT_API_KEY", "7NQUQLwEbraW-VrkS0RXMw")

func main() {

	router := mux.NewRouter()

	router.HandleFunc("/v1/chat/completions", chatCompletionHandler).Methods("POST")
	router.HandleFunc("/v1/completions", completionHandler).Methods("POST")

	fmt.Println("App started " + koboldAPIURL)
	http.ListenAndServe(":8080", router)
}

func chatCompletionHandler(w http.ResponseWriter, r *http.Request) {
	apiKey := r.Header.Get("Authorization")
	if apiKey == "" {
		apiKey = defaultAPIKey
	} else {
		apiKey = strings.TrimPrefix(apiKey, "Bearer ")
	}

	var chatReq openAIChatRequest
	if err := json.NewDecoder(r.Body).Decode(&chatReq); err != nil {
		fmt.Fprintf(os.Stderr, "Error decoding request body: %v", err)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	koboldReq := convertOpenAIChatRequestToKobold(chatReq)
	koboldResp, err := callKoboldAPI(koboldReq, apiKey)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error calling Kobold API: %v", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	chatResp := convertKoboldResponseToOpenAIChatResponse(koboldResp)

	fmt.Fprintln(os.Stdout, chatResp)

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(chatResp)
}

func completionHandler(w http.ResponseWriter, r *http.Request) {
	apiKey := r.Header.Get("Authorization")
	if apiKey == "" {
		apiKey = defaultAPIKey
	} else {
		apiKey = strings.TrimPrefix(apiKey, "Bearer ")
	}

	var completionReq openAICompletionRequest
	if err := json.NewDecoder(r.Body).Decode(&completionReq); err != nil {
		fmt.Fprintln(os.Stderr, err)
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	koboldReq := convertOpenAICompletionRequestToKobold(completionReq)
	koboldResp, err := callKoboldAPI(koboldReq, apiKey)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	completionResp := convertKoboldResponseToOpenAICompletionResponse(koboldResp)
	fmt.Printf("Completion Response: %+v\n", completionResp)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(completionResp)
}
