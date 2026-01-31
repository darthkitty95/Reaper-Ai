import socket
import subprocess

class StealthGuard:
    @staticmethod
    def is_tor_active():
        """Checks if the Tor SOCKS proxy is listening on the default port."""
        try:
            # Try to connect to Tor's default SOCKS port
            with socket.create_connection(("127.0.0.1", 9050), timeout=2):
                return True
        except (socket.timeout, ConnectionRefusedError):
            return False

    @staticmethod
    def get_current_ip():
        """Fetches public IP to verify it is not the local ISP address."""
        try:
            # This request should be routed through proxychains if called by the AI
            res = subprocess.check_output("curl -s https://checkip.amazonaws.com", shell=True, text=True)
            return res.strip()
        except:
            return "Unknown"

    def verify_killswitch(self):
        if not self.is_tor_active():
            print("!!! STEALTH KILL-SWITCH TRIGGERED: Tor is not running. !!!")
            return False
        return True
