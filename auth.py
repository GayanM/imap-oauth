# auth.py

import msal
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from config import CLIENT_ID, AUTHORITY, REDIRECT_URI, SCOPES

redirect_result = None


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global redirect_result

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # Capture full redirect response (code + state)
        redirect_result = {
            "code": params.get("code", [None])[0],
            "state": params.get("state", [None])[0]
        }

        if redirect_result["code"]:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Login successful. You may close this window.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Authorization failed.")


def get_access_token():
    global redirect_result
    redirect_result = None

    def start_server():
        server = HTTPServer(("localhost", 8000), AuthHandler)
        server.handle_request()
        server.server_close()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY
    )

    # PKCE handled automatically
    flow = app.initiate_auth_code_flow(
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url = flow["auth_uri"]

    print("Opening browser for login...")
    webbrowser.open(auth_url)

    server_thread.join()

    if not redirect_result or not redirect_result.get("code"):
        raise Exception("Failed to capture authorization response")

    # MSAL validates state + PKCE automatically
    result = app.acquire_token_by_auth_code_flow(
        flow,
        redirect_result
    )

    if "access_token" not in result:
        raise Exception(result)

    return result["access_token"]