package main

import (
	_ "github.com/google/uuid"
)

type openAIChatRequest struct {
	Model    string              `json:"model"`
	Messages []openAIChatMessage `json:"messages"`
}

type openAIChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type openAICompletionRequest struct {
	Model       string   `json:"model"`
	Prompt      string   `json:"prompt"`
	MaxTokens   int      `json:"max_tokens"`
	Temperature float64  `json:"temperature"`
	TopP        float64  `json:"top_p"`
	N           int      `json:"n"`
	Stream      bool     `json:"stream"`
	Logprobs    *int     `json:"logprobs,omitempty"`
	Stop        []string `json:"stop,omitempty"`
}

type openAIChatResponse struct {
	ID      string             `json:"id"`
	Object  string             `json:"object"`
	Created int                `json:"created"`
	Choices []openAIChatChoice `json:"choices"`
	Usage   openAIUsage        `json:"usage"`
}

type openAIChatChoice struct {
	Index        int               `json:"index"`
	Message      openAIChatMessage `json:"message"`
	FinishReason string            `json:"finish_reason"`
}

type openAIUsage struct {
	PromptTokens     int `json:"prompt_tokens"`
	CompletionTokens int `json:"completion_tokens"`
	TotalTokens      int `json:"total_tokens"`
}

type openAICompletionResponse struct {
	ID      string                   `json:"id"`
	Object  string                   `json:"object"`
	Created int                      `json:"created"`
	Model   string                   `json:"model"`
	Choices []openAICompletionChoice `json:"choices"`
	Usage   openAIUsage              `json:"usage"`
}

type openAICompletionChoice struct {
	Text         string      `json:"text"`
	Index        int         `json:"index"`
	Logprobs     interface{} `json:"logprobs,omitempty"`
	FinishReason string      `json:"finish_reason"`
}

type koboldAIRequest struct {
	Prompt         string   `json:"prompt"`
	Models         []string `json:"models"`
	TrustedWorkers bool     `json:"trusted_workers"`
	Params         params   `json:"params"`
}

type params struct {
	MaxContextLength int `json:"max_context_length"`
	MaxLength        int `json:"max_length"`
}

type koboldAIPollResponse struct {
	Finished      int          `json:"finished"`
	Processing    int          `json:"processing"`
	Restarted     int          `json:"restarted"`
	Waiting       int          `json:"waiting"`
	Done          bool         `json:"done"`
	Faulted       bool         `json:"faulted"`
	WaitTime      int          `json:"wait_time"`
	QueuePosition int          `json:"queue_position"`
	Kudos         float32      `json:"kudos"`
	IsPossible    bool         `json:"is_possible"`
	Generations   []generation `json:"generations"`
}

type generation struct {
	WorkerID   string `json:"worker_id"`
	WorkerName string `json:"worker_name"`
	Model      string `json:"model"`
	State      string `json:"state"`
	Text       string `json:"text"`
	Seed       int    `json:"seed"`
}

type koboldAIAsyncResponse struct {
	ID      string `json:"id"`
	Message string `json:"message"`
}
