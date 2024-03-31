import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import utils

default_api_key = "0000000000"
#mine: F1zmplJTUjd2vJoMB-qGhA

def do_POST(self):
    api_key = self.headers.get("Authorization")
    if api_key is None:
        api_key = default_api_key
    else:
        api_key = api_key.replace("Bearer ", "")

    content_length = int(self.headers.get("Content-Length", 0))
    body = self.rfile.read(content_length).decode("utf-8")

    try:
        chat_req = json.loads(body)
    except json.JSONDecodeError as e:
        self.send_error(400, f"Error decoding request body: {str(e)}")
        return

    kobold_req = convert_openai_chat_request_to_kobold(chat_req)  #David done this
    try:
        kobold_resp = call_kobold_api(kobold_req, api_key)  #step 3
    except Exception as e:
        self.send_error(500, f"Error calling Kobold API: {str(e)}")
        return

    chat_resp = convert_kobold_response_to_openai_chat_response(kobold_resp)   #Next step 2

    print(chat_resp)

    self.send_response(200)
    self.send_header("Content-Type", "application/json")
    self.end_headers()
    self.wfile.write(json.dumps(chat_resp).encode("utf-8"))

do_POST()
