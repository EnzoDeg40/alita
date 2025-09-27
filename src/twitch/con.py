import os
import socket
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import dotenv
import requests

dotenv.load_dotenv(override=True)

# --------------------------
# TWITCH CONFIGURATION
# --------------------------
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:3000")
CHANNEL = os.getenv("CHANNEL")

AUTH_URL = "https://id.twitch.tv/oauth2/authorize?" + urllib.parse.urlencode(
    {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "chat:read chat:edit",
    }
)

TOKEN = None


# --------------------------
# HTTP SERVER TO RETRIEVE THE CODE
# --------------------------
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global TOKEN
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            code = params["code"][0]
            # Exchange the code for a token
            resp = requests.post(
                "https://id.twitch.tv/oauth2/token",
                params={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": REDIRECT_URI,
                },
            )
            data = resp.json()
            TOKEN = data.get("access_token")
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                "<h1>Authentication successful!</h1> You can close this page.".encode(
                    "utf-8"
                )
            )
        else:
            self.send_response(400)
            self.end_headers()


def run_server():
    httpd = HTTPServer(("localhost", 3000), OAuthHandler)
    httpd.handle_request()  # only one request


# --------------------------
# TWITCH IRC CONNECTION
# --------------------------
def connect_chat(token):
    server = "irc.chat.twitch.tv"
    port = 6667
    nickname = CHANNEL
    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS oauth:{token}\r\n".encode("utf-8"))
    sock.send(f"NICK {nickname}\r\n".encode("utf-8"))
    sock.send(f"JOIN #{CHANNEL}\r\n".encode("utf-8"))
    print(f"✅ Connected to #{CHANNEL} chat")

    while True:
        resp = sock.recv(2048).decode("utf-8", errors="ignore")
        if resp.startswith("PING"):
            sock.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        else:
            parts = resp.split(":", 2)
            if len(parts) > 2 and "PRIVMSG" in parts[1]:
                username = parts[1].split("!")[0]
                message = parts[2]
                print(f"{username}: {message.strip()}")


if __name__ == "__main__":
    print("➡️ Opening browser for Twitch authorization...")
    threading.Thread(target=run_server, daemon=True).start()
    webbrowser.open(AUTH_URL)

    # Wait for token access
    while TOKEN is None:
        pass

    print("🔑 Token received, connecting to chat...")
    connect_chat(TOKEN)
