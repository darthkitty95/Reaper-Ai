# Stealth Header added by AI Agent
import socks
import socket
import requests

# Force all global traffic through Tor
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket

# Verify anonymity before main logic
if requests.get('https://checkip.amazonaws.com').text.strip() == "YOUR_REAL_IP":
    raise SystemExit("Stealth Failure: Real IP detected. Shutting down.")


