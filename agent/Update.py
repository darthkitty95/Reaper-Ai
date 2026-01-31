#!/usr/bin/python3
import os
import sys
import json
import subprocess
import requests
from bs4 import BeautifulSoup
from datetime import datetime

class EvolvingKatoolin:
    def __init__(self):
        self.sources_path = "/etc/apt/sources.list"
        self.brain_file = "assistant_brain.json"
        self.default_tools_url = "https://www.kali.org/tools/all-tools/"
        self.knowledge_base = {
            "categories": {
                "recon": ["nmap", "dnsrecon", "theharvester"],
                "web": ["sqlmap", "burpsuite", "wpscan"],
                "wireless": ["aircrack-ng", "reaver", "wifite"]
            },
            "last_crawl": None,
            "discovered_tools": []
        }
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.brain_file):
            with open(self.brain_file, "r") as f:
                self.knowledge_base.update(json.load(f))

    def _save_memory(self):
        with open(self.brain_file, "w") as f:
            json.dump(self.knowledge_base, f, indent=4)

    def evolve(self):
        """Scrapes official Kali site to discover new tools."""
        print("\033[1;34m[*] Evolving... Scanning official Kali toolsets...\033[1;m")
        try:
            response = requests.get(self.default_tools_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extracting tool names from the Kali tools page structure
            tools = [a.text.strip() for a in soup.find_all('h5')]
            
            new_count = 0
            for tool in tools:
                if tool not in self.knowledge_base["discovered_tools"]:
                    self.knowledge_base["discovered_tools"].append(tool)
                    new_count += 1
            
            self.knowledge_base["last_crawl"] = datetime.now().strftime("%Y-%m-%d")
            self._save_memory()
            print(f"\033[1;32m[+] Evolution complete. Discovered {new_count} new tools.\033[1;m")
        except Exception as e:
            print(f"\033[1;31m[!] Evolution failed: {e}\033[1;m")

    def execute_sys(self, command):
        print(f"\033[1;33m[AI Executing]: {command}\033[1;m")
        subprocess.run(command, shell=True)

    def handle_request(self, user_input):
        user_input = user_input.lower()

        if "evolve" in user_input or "update brain" in user_input:
            self.evolve()
            return "Knowledge base updated with the latest tools from Kali.org."

        if "install" in user_input:
            # Smart Lookup: Check if the tool exists in discovered tools
            for tool in self.knowledge_base["discovered_tools"]:
                if tool.lower() in user_input:
                    self.execute_sys(f"apt-get install -y {tool.lower()}")
                    return f"Successfully installed {tool}."
            
            # Fallback for manual install
            parts = user_input.split()
            if "install" in parts:
                target = parts[parts.index("install") + 1]
                self.execute_sys(f"apt-get install -y {target}")
                return f"Attempted manual install of {target}."

        return "I am ready. Commands: 'evolve', 'install [tool]', 'exit'."

# --- MAIN LOOP ---
if __name__ == "__main__":
    if os.getuid() != 0:
        print("Root privileges required.")
        sys.exit()

    # Ensure dependencies are met for the living script
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("Installing script dependencies...")
        subprocess.run("pip3 install requests beautifulsoup4", shell=True)

    bot = EvolvingKatoolin()
    print("\033[1;35m--- LIVING KATOOLIN AI v4.0 ---\033[1;m")
    
    while True:
        cmd = input("\033[1;36mAI > \033[1;m").strip()
        if cmd.lower() in ['exit', 'quit']: break
        print(bot.handle_request(cmd))
