import json
import uuid
import requests
import time

#UNTESTED, but main structure here

def convert_openai_chat_request_to_kobold(chat_req):
    prompt = ""
    for message in chat_req["messages"]:
        prompt += message["role"] + ": " + message["content"] + "\n"
    prompt += "assistant: "

    return {
        "prompt": prompt,
        "models": [chat_req["model"]],
        "trusted_workers": False,
        "params": {
            "max_context_length": 2048,
            "max_length": 100
        }
    }

def convert_openai_completion_request_to_kobold(completion_req):
    return {
        "prompt": completion_req["prompt"],
        "models": [completion_req["model"]],
        "trusted_workers": False,
        "params": {
            "max_context_length": 2048,
            "max_length": completion_req["max_tokens"]
        }
    }
    
#this is tested
def convert_openai_completion_request_to_kobold(payload: OpenAICompletionRequest) -> KoboldAIRequest:
    return KoboldAIRequest(
        prompt=payload.prompt,
        models=[payload.model],
        trusted_workers=True,
        params=Params(max_context_length=1, max_length=1)
    )

def call_kobold_api(kobold_req, api_key):
    print(f"Req: {kobold_req}")
    req_body = json.dumps(kobold_req)

    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }

    resp = requests.post(kobold_api_url, data=req_body, headers=headers)
    print("Sending request to horde")

    json_response = resp.json()
    print(f"Resp: {json_response}")

    print("Polling horde with job id", json_response["id"])
    result = poll_kobold_api(json_response["id"])

    return result

def poll_kobold_api(job_id):
    status_endpoint = kobold_status_url + job_id

    while True:
        time.sleep(2)

        resp = requests.get(status_endpoint)
        json_response = resp.json()
        print(json_response)
        print(f"Resp: {json_response}")

        if json_response["done"]:
            return json_response

def convert_kobold_response_to_openai_chat_response(kobold_resp):
    full_response_text = kobold_resp["generations"][0]["text"]
    response_text = full_response_text

    if response_text == "":
        return {}

    assistant_message = {
        "role": "assistant",
        "content": response_text
    }

    return {
        "id": str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "choices": [
            {
                "index": 0,
                "message": assistant_message,
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(full_response_text),
            "completion_tokens": len(response_text),
            "total_tokens": len(full_response_text) + len(response_text)
        }
    }

def convert_kobold_response_to_openai_completion_response(kobold_resp):
    response_text = kobold_resp["generations"][0]["text"]

    return {
        "id": str(uuid.uuid4()),
        "object": "text.completion",
        "created": int(time.time()),
        "choices": [
            {
                "text": response_text,
                "index": 0,
                "logprobs": None,
                "finish_reason": "stop"
            }
        ],
        "model": kobold_resp["generations"][0]["model"],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }
