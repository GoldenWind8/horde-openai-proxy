import sys

from fastapi import FastAPI, HTTPException, Header
from utils import *
from models import *

app = FastAPI()
default_api_key = "0000000000"
base_url = "https://api.aipowergrid.io/api/v2/generate/text/"
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/v1/chat/completions")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.post("/v1/completions")
async def completion_handler(
    request: OpenAICompletionRequest,
    authorization: Optional[str] = Header(default_api_key),
):
    api_key = authorization or default_api_key
    if api_key.startswith("Bearer "):
        api_key = api_key[len("Bearer "):]


    kobold_req = convert_openai_completion_request_to_kobold(request)
    kobold_resp = None
    try:
        kobold_resp = call_kobold_api(kobold_req, base_url, api_key)
    except Exception as e:
        print(f"Error calling Kobold API: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

    completion_oai = convert_kobold_response_to_openai_completion_response(kobold_resp)

    print(completion_oai.choices[0].text)

    return completion_oai
