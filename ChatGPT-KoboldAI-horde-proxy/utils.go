package main

import (
	"encoding/json"
	"fmt"
	"github.com/google/uuid"
	"net/http"
	"os"
	"runtime"
	"strings"
	"time"
)

func convertOpenAIChatRequestToKobold(chatReq openAIChatRequest) koboldAIRequest {

	prompt := ""
	for _, message := range chatReq.Messages {
		prompt += message.Role + ": " + message.Content + "\n"
	}
	prompt += "assistant: "

	return koboldAIRequest{
		Prompt:         prompt,
		Models:         []string{chatReq.Model},
		TrustedWorkers: false,
		Params: params{
			MaxContextLength: 2048,
			MaxLength:        100,
		},
	}
}

func convertOpenAICompletionRequestToKobold(completionReq openAICompletionRequest) koboldAIRequest {
	return koboldAIRequest{
		Prompt:         completionReq.Prompt,
		Models:         []string{completionReq.Model},
		TrustedWorkers: false,
		Params: params{
			MaxContextLength: 2048,
			MaxLength:        completionReq.MaxTokens,
		},
	}
}

func callKoboldAPI(koboldReq koboldAIRequest, apiKey string) (koboldAIPollResponse, error) {
	fmt.Printf("Req: %+v\n", koboldReq)
	reqBody, err := json.Marshal(koboldReq)
	if err != nil {
		_, file, line, _ := runtime.Caller(0)
		errMsg := fmt.Sprintf("Error while marshal request at %s:%d: %v", file, line, err)
		fmt.Fprintln(os.Stderr, errMsg)
		return koboldAIPollResponse{}, err
	}

	req, err := http.NewRequest("POST", koboldAPIURL, strings.NewReader(string(reqBody)))
	if err != nil {
		_, file, line, _ := runtime.Caller(0)
		errMsg := fmt.Sprintf("Error while creating request at %s:%d: %v", file, line, err)
		fmt.Fprintln(os.Stderr, errMsg)
		return koboldAIPollResponse{}, err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("apikey", apiKey)

	client := &http.Client{}
	resp, err := client.Do(req)
	fmt.Fprintln(os.Stdout, "Sending request to horde")
	if err != nil {
		_, file, line, _ := runtime.Caller(0)
		errMsg := fmt.Sprintf("Error while querying horde at %s:%d: %v", file, line, err)
		fmt.Fprintln(os.Stderr, errMsg)
		return koboldAIPollResponse{}, err
	}
	defer resp.Body.Close()

	var jsonResponse koboldAIAsyncResponse
	err = json.NewDecoder(resp.Body).Decode(&jsonResponse)
	if err != nil {
		_, file, line, _ := runtime.Caller(0)
		errMsg := fmt.Sprintf("Error occurred at %s:%d: %v", file, line, err)
		fmt.Fprintln(os.Stderr, errMsg)
		return koboldAIPollResponse{}, err
	}
	fmt.Printf("Resp: %+v\n", jsonResponse)

	fmt.Fprintln(os.Stdout, "Polling horde with job id ", jsonResponse.ID)
	result, err := pollKoboldAPI(jsonResponse.ID)
	if err != nil {
		errMsg := fmt.Sprintf("Error polling horde: %v", err)
		fmt.Fprintln(os.Stderr, errMsg)
		return koboldAIPollResponse{}, err
	}

	return result, nil
}

func pollKoboldAPI(id string) (koboldAIPollResponse, error) {
	statusEndpoint := koboldStatusURL + id

	for {
		time.Sleep(2 * time.Second)

		resp, err := http.Get(statusEndpoint)
		if err != nil {
			errMsg := fmt.Sprintf("Error polling horde GET: %v", err)
			fmt.Fprintln(os.Stderr, errMsg)
			return koboldAIPollResponse{}, err
		}
		defer resp.Body.Close()

		var jsonResponse koboldAIPollResponse
		fmt.Fprintln(os.Stdout, jsonResponse)
		err = json.NewDecoder(resp.Body).Decode(&jsonResponse)
		if err != nil {
			errMsg := fmt.Sprintf("Error polling horde decode: %v", err)
			fmt.Fprintln(os.Stderr, errMsg)
			return koboldAIPollResponse{}, err
		}
		fmt.Printf("Resp: %+v\n", jsonResponse)

		if jsonResponse.Done {
			return jsonResponse, nil
		}
	}
}

func convertKoboldResponseToOpenAIChatResponse(koboldResp koboldAIPollResponse) openAIChatResponse {
	// Get the full text of the response
	fullResponseText := koboldResp.Generations[0].Text
	var responseText string = fullResponseText

	//TODO fix assistant expectant logic.

	// Look for the first 'assistant' line and remove the 'assistant:' prefix
	//lines := strings.Split(fullResponseText, "\n")
	//for _, line := range lines {
	//	if strings.HasPrefix(line, "assistant: ") {
	//		responseText = strings.TrimPrefix(line, "assistant: ")
	//		break
	//	}
	//}

	// If no 'assistant' line is found, there's no assistant response to return
	if responseText == "" {
		return openAIChatResponse{}
	}

	assistantMessage := openAIChatMessage{
		Role:    "assistant",
		Content: responseText,
	}

	id, _ := uuid.NewUUID()
	return openAIChatResponse{
		ID:      id.String(),
		Object:  "chat.completion",
		Created: int(time.Now().Unix()),
		Choices: []openAIChatChoice{
			{
				Index:        0,
				Message:      assistantMessage,
				FinishReason: "stop",
			},
		},
		Usage: openAIUsage{
			PromptTokens:     len(fullResponseText),
			CompletionTokens: len(responseText),
			TotalTokens:      len(fullResponseText) + len(responseText),
		},
	}
}

func convertKoboldResponseToOpenAICompletionResponse(koboldResp koboldAIPollResponse) openAICompletionResponse {
	responseText := koboldResp.Generations[0].Text

	id, _ := uuid.NewUUID()
	return openAICompletionResponse{
		ID:      id.String(),
		Object:  "text.completion",
		Created: int(time.Now().Unix()),
		Choices: []openAICompletionChoice{
			{
				Text:         responseText,
				Index:        0,
				Logprobs:     nil,
				FinishReason: "stop",
			},
		},
		Model: koboldResp.Generations[0].Model,
		Usage: openAIUsage{
			PromptTokens:     0,
			CompletionTokens: 0,
			TotalTokens:      0,
		},
	}
}
