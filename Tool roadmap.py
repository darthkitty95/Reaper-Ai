import asyncio
import nmap3 # Modern Nmap wrapper
import aiohttp # Asynchronous HTTP for web hacking
import json
from datetime import datetime

class EthicalHackingSuite:
    def __init__(self, target):
        self.target = target
        self.results = {
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "recon": {},
            "vulns": []
        }

    # --- 🕵️‍♂️ MODERN RECON (Information Gathering) ---
    async def run_recon(self):
        print(f"[*] Starting Modern Recon on {self.target}...")
        nmap = nmap3.NmapHostDiscovery()
        # High-speed port scanning
        self.results["recon"] = nmap.nmap_portscan_only(self.target)
        print("[+] Recon Complete.")

    # --- 🚀 WEB HACKING (Vulnerability Scanning) ---
    async def check_web_vulns(self):
        print(f"[*] Testing Web Entry Points...")
        # Simulating a modern template-based vulnerability check
        async with aiohttp.ClientSession() as session:
            paths = ["/.env", "/api/v1/config", "/.git/config"]
            for path in paths:
                async with session.get(f"http://{self.target}{path}") as resp:
                    if resp.status == 200:
                        self.results["vulns"].append({"path": path, "status": "EXPOSED"})
        print("[+] Web Scan Complete.")

    # --- 🎉 POST-EXPLOITATION (Data Aggregation) ---
    def generate_report(self):
        filename = f"report_{self.target}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(f"[!] Intelligence Report saved to {filename}")

# --- ⚙️ INTEGRATION ENGINE ---
async def main():
    target_ip = "127.0.0.1" # Change to your authorized target
    suite = EthicalHackingSuite(target_ip)
    
    # Run all modules concurrently
    await asyncio.gather(
        suite.run_recon(),
        suite.check_web_vulns()
    )
    
    suite.generate_report()

if __name__ == "__main__":
    asyncio.run(main())



