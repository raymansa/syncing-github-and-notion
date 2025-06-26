import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:3000"

def get_github_token():
    """
    Orchestrates the OAuth2 flow to get a user token for the GitHub API.
    This requires manual user interaction in a browser.
    """
    auth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo,project&redirect_uri={REDIRECT_URI}"
    
    print("Your browser will now open to authorize this application.")
    print(f"If it doesn't, please open this URL manually:\n{auth_url}")
    webbrowser.open(auth_url)

    # A simple local server to catch the redirect
    class OAuthCallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            if "code" in query_params:
                self.server.auth_code = query_params["code"][0]
                self.wfile.write(b"<h1>Authentication successful!</h1><p>You can close this window now.</p>")
            else:
                self.server.auth_code = None
                self.wfile.write(b"<h1>Authentication failed.</h1>")

    server = HTTPServer(('localhost', 3000), OAuthCallbackHandler)
    server.auth_code = None
    
    print("Waiting for GitHub authorization callback on http://localhost:3000...")
    while server.auth_code is None:
        server.handle_request()

    # Exchange the authorization code for an access token
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": server.auth_code,
    }
    headers = {"Accept": "application/json"}
    response = requests.post(token_url, json=payload, headers=headers)
    
    return response.json().get("access_token")