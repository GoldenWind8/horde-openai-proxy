import uuid
import requests
import time
from parser import parse_messages

from fastapi import HTTPException

from models import *

def convert_openai_chat_request_to_kobold(payload: OpenAIChatRequest) -> KoboldAIRequest:
    prompt = parse_messages(payload.messages)

    return KoboldAIRequest(
        prompt=prompt,
        models=[payload.model],
        trusted_workers=False,
        params=Params(max_context_length=512, max_length=payload.max_tokens, temperature=payload.temperature,
                      top_p=payload.top_p, stop_sequence = payload.stop)
    )

def convert_openai_completion_request_to_kobold(payload: OpenAICompletionRequest) -> KoboldAIRequest:
    prompt = payload.prompt
    if isinstance(prompt, list):
        prompt = prompt[0]

    print(prompt)

    return KoboldAIRequest(
        prompt=prompt,
        models=[payload.model],
        trusted_workers=False,
        params=Params(max_context_length=512, max_length=payload.max_tokens, temperature=payload.temperature, top_p = payload.top_p )
    )

def call_kobold_api(kobold_req: KoboldAIRequest, base_url, api_key) -> KoboldAIPollResponse:
    print(f"Kobold Req: {kobold_req.json()}")
    req_body = kobold_req.json()

    headers = {
        "Content-Type": "application/json",
        "apikey": api_key
    }

    resp = requests.post(base_url+"async", data=req_body, headers=headers)
    json_response = resp.json()

    print(f"Grid Resp: {json_response}")
    if "id" not in json_response:
        raise HTTPException(status_code=500, detail=str(json_response))
    print("Polling horde with job id", json_response["id"])
    result = poll_kobold_api(json_response["id"], base_url)

    kobold_res = KoboldAIPollResponse(**result)
    return kobold_res

def poll_kobold_api(job_id, base_url):
    status_endpoint = base_url + "status/"+ job_id

    while True:
        time.sleep(2)

        resp = requests.get(status_endpoint)
        json_response = resp.json()
        print(f"Polled Resp: {json_response}")

        if json_response["done"]:
            return json_response

def convert_kobold_response_to_openai_chat_response(kobold_resp: KoboldAIPollResponse) -> OpenAIChatResponse:
    full_response_text = kobold_resp.generations[0].text
    response_text = full_response_text

    if response_text == "":
        return OpenAIChatResponse(
            id=str(uuid.uuid4()),
            object="chat.completion",
            created=int(time.time()),
            choices=[],
            usage=OpenAIUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        )

    assistant_message = OpenAIChatMessage(role="assistant", content=response_text)

    return OpenAIChatResponse(
        id=str(uuid.uuid4()),
        object="chat.completion",
        created=int(time.time()),
        choices=[
            OpenAIChatChoice(
                index=0,
                message=assistant_message,
                finish_reason="stop"
            )
        ],
        usage=OpenAIUsage(
            prompt_tokens=len(full_response_text),
            completion_tokens=len(response_text),
            total_tokens=len(full_response_text) + len(response_text)
        )
    )

def convert_kobold_response_to_openai_completion_response(kobold_resp: KoboldAIPollResponse) -> OpenAICompletionResponse:
    response_text = kobold_resp.generations[0].text

    return OpenAICompletionResponse(
        id=str(uuid.uuid4()),
        object="text.completion",
        created=int(time.time()),
        choices=[
            OpenAICompletionChoice(
                text=response_text,
                index=0,
                logprobs=None,
                finish_reason="stop"
            )
        ],
        model=kobold_resp.generations[0].model,
        usage=OpenAIUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        )
    )
