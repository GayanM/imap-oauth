# auth.py

import msal
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from config import CLIENT_ID, CLIENT_SECRET, AUTHORITY, REDIRECT_URI, SCOPES

auth_code = None


class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code

        params = parse_qs(urlparse(self.path).query)

        if "code" in params:
            auth_code = params["code"][0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Login successful. You may close this window.")
        else:
            self.send_response(400)
            self.end_headers()


def get_access_token():
    global auth_code

    def start_server():
        server = HTTPServer(("localhost", 8000), AuthHandler)
        server.handle_request()
        server.server_close()

    server_thread = threading.Thread(target=start_server)
    server_thread.start()

    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET
    )

    auth_url = app.get_authorization_request_url(
        SCOPES,
        redirect_uri=REDIRECT_URI
    )

    print("Opening browser for login...")
    webbrowser.open(auth_url)

    server_thread.join()

    if not auth_code:
        raise Exception("Failed to capture authorization code")

    result = app.acquire_token_by_authorization_code(
        auth_code,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    if "access_token" not in result:
        raise Exception(result)

    return result["access_token"]