#!/usr/bin/python3
import os
import sys
import json
import subprocess
from datetime import datetime

class LivingKatoolin:
    def __init__(self):
        self.sources_path = "/etc/apt/sources.list"
        self.log_file = "assistant_learning.log"
        # The "Knowledge Base" that grows over time
        self.knowledge_base = {
            "recon": ["nmap", "dnsrecon", "theharvester"],
            "web": ["sqlmap", "burpsuite", "wpscan"],
            "wireless": ["aircrack-ng", "reaver", "wifite"],
            "repo_added": False
        }
        self._load_memory()

    def _load_memory(self):
        """Loads previous learning data if it exists."""
        if os.path.exists("brain.json"):
            with open("brain.json", "r") as f:
                self.knowledge_base.update(json.load(f))

    def _save_memory(self):
        """Saves new tools/categories learned during the session."""
        with open("brain.json", "w") as f:
            json.dump(self.knowledge_base, f)

    def log_action(self, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {action}\n")

    def execute(self, cmd):
        """Safety wrapper for system execution."""
        try:
            print(f"\033[1;33m[Executing]: {cmd}\033[1;m")
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"

    # --- CORE ABILITIES ---
    def setup_repos(self):
        """Adds Kali repositories and keys."""
        print("Integrating Kali Repositories...")
        self.execute("apt-key adv --keyserver keyserver.ubuntu.com --recv-keys ED444FF07D8D0BF6")
        with open(self.sources_path, "a") as f:
            f.write("\n# Added by Living Assistant\ndeb http://http.kali.org/kali kali-rolling main contrib non-free\n")
        self.knowledge_base["repo_added"] = True
        self._save_memory()
        return self.execute("apt-get update")

    def learn_and_install(self, category, tool_name):
        """The 'Learning' part: adds new tools to the brain if not present."""
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
            print(f"Learned new category: {category}")
        
        if tool_name not in self.knowledge_base[category]:
            self.knowledge_base[category].append(tool_name)
            print(f"Learned new tool: {tool_name}")
        
        self._save_memory()
        self.log_action(f"Installed {tool_name} in {category}")
        return self.execute(f"apt-get install -y {tool_name}")

    def process_natural_language(self, user_input):
        """Basic intent parser to act like an assistant."""
        user_input = user_input.lower()
        
        if "setup" in user_input or "repository" in user_input:
            return self.setup_repos()
        
        if "install" in user_input:
            # Simple extraction logic
            words = user_input.split()
            # Logic: 'install [tool] for [category]'
            try:
                tool = words[words.index("install") + 1]
                category = words[words.index("for") + 1] if "for" in words else "uncategorized"
                return self.learn_and_install(category, tool)
            except (IndexError, ValueError):
                return "I heard 'install', but I need to know what tool. Try: 'install nmap for recon'"

        return "I'm learning! You can tell me to 'setup repos' or 'install [tool] for [category]'."

# --- INTEGRATION LOOP ---
if __name__ == "__main__":
    if os.getuid() != 0:
        print("Please run with sudo.")
        sys.exit()

    assistant = LivingKatoolin()
    print("\033[1;32mLiving Katoolin AI Assistant Online.\033[1;m")
    
    while True:
        query = input("\033[1;36mHow can I help you today? > \033[1;m")
        if query.lower() in ["exit", "quit"]:
            break
        response = assistant.process_natural_language(query)
        print(response)

