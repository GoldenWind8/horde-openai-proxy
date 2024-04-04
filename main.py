import sys
from dotenv import load_dotenv
import os

from fastapi import FastAPI, HTTPException, Header
from fastapi.openapi.models import Response
from starlette.responses import JSONResponse

from utils import *
from models import *

load_dotenv()  # Load environment variables from .env file
app = FastAPI()
default_api_key = os.getenv("API_KEY", "0000000000")
base_url = os.getenv("BASE_URL", "")
textgen_url = base_url  + "/api/v2/generate/text/"

@app.get("/health")
async def health():
    return {"status": "OK"}

@app.get("/v1/models")
async def show_available_models():
    models = ["Mistral", "Mixtral", "DBRX"]
    return JSONResponse(content=models)


@app.post("/v1/chat/completions")
async def chat_handler(
        request: OpenAIChatRequest,
        authorization: Optional[str] = Header(default_api_key),
):
    api_key = authorization or default_api_key
    if api_key.startswith("Bearer "):
        api_key = api_key[len("Bearer "):]

    kobold_req = convert_openai_chat_request_to_kobold(request)
    kobold_resp = None
    try:
        kobold_resp = call_kobold_api(kobold_req, textgen_url, api_key)
    except Exception as e:
        print(f"Error calling Kobold API: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

    chat_oai = convert_kobold_response_to_openai_chat_response(kobold_resp)

#    print(chat_oai.choices[0].message.content)

    return chat_oai

@app.post("/v1/completions")
async def completion_handler(
        request: OpenAICompletionRequest,
        authorization: Optional[str] = Header(default_api_key),
):
    api_key = authorization or default_api_key
    if api_key.startswith("Bearer "):
        api_key = api_key[len("Bearer "):]
    print(2)
    kobold_req = convert_openai_completion_request_to_kobold(request)
    kobold_resp = None
    try:
        kobold_resp = call_kobold_api(kobold_req, textgen_url, api_key)
    except Exception as e:
        print(f"Error calling Kobold API: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

    completion_oai = convert_kobold_response_to_openai_completion_response(kobold_resp)

    print(completion_oai.choices[0].text)

    return completion_oai
