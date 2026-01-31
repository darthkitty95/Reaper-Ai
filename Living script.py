#!/usr/bin/python3
import os
import sys
import json
import subprocess
import re
import yaml
import time
import sqlite3
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path

# Note: Requires 'pip install GitPython PyYAML openai'
try:
    from git import Repo
    import openai
except ImportError:
    print("Missing dependencies. Run: pip install GitPython PyYAML openai")

class LivingKatoolin:
    def __init__(self, config_path="config.yaml"):
        self.sources_path = "/etc/apt/sources.list"
        self.log_file = "assistant_learning.log"
        self.config_path = Path(config_path)
        
        # Load Config from YAML (from config 2.yaml)
        self.cfg = self._load_config()
        
        # Knowledge Base (Memory)
        self.knowledge_base = {
            "recon": ["nmap", "dnsrecon", "theharvester"],
            "web": ["sqlmap", "burpsuite", "wpscan"],
            "wireless": ["aircrack-ng", "reaver", "wifite"],
            "repo_added": False
        }
        self._load_memory()
        
        # Initialize Agent Components
        self.db_path = Path(self.cfg.get("knowledge_db", "./agent_data/knowledge.db"))
        self._ensure_db_table()
        
        if self.cfg.get("llm_provider") == "openai":
            self._init_openai()

    # --- CONFIG & MEMORY ---
    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        return {
            "watch_path": "./target_project",
            "llm_provider": "openai",
            "llm_model": "gpt-4o-mini",
            "dry_run": True,
            "require_approval": True
        }

    def _load_memory(self):
        if os.path.exists("brain.json"):
            with open("brain.json", "r") as f:
                self.knowledge_base.update(json.load(f))

    def _save_memory(self):
        with open("brain.json", "w") as f:
            json.dump(self.knowledge_base, f)

    # --- DATABASE OPERATIONS (from agent_knowledge) ---
    def _ensure_db_table(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS examples (
                id TEXT PRIMARY KEY, diagnostic TEXT, patch TEXT, metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

    def add_to_db(self, diagnostic_dict, patch, metadata=None):
        conn = sqlite3.connect(str(self.db_path))
        diag_json = json.dumps(diagnostic_dict)
        mid = hashlib.sha256((diag_json + patch).encode("utf-8")).hexdigest()
        conn.execute("INSERT OR IGNORE INTO examples VALUES (?, ?, ?, ?)",
                    (mid, diag_json, patch, json.dumps(metadata or {})))
        conn.commit()
        conn.close()

    # --- LLM OPERATIONS (from agent_llm_client) ---
    def _init_openai(self):
        key = os.getenv("OPENAI_API_KEY")
        if key:
            openai.api_key = key

    def get_llm_fix(self, prompt):
        try:
            resp = openai.ChatCompletion.create(
                model=self.cfg.get("llm_model", "gpt-4o-mini"),
                messages=[{"role": "system", "content": "You are a helpful code assistant."},
                          {"role": "user", "content": prompt}],
                temperature=0.0
            )
            text = resp["choices"][0]["message"]["content"]
            return None if "NO_PATCH" in text else text
        except Exception as e:
            self.log_action(f"LLM Error: {e}")
            return None

    # --- PATCHING LOGIC (from agent_patcher) ---
    def apply_patch(self, patch_text, file_path):
        print(f"\n[!] Suggested patch for {file_path}:")
        print(patch_text[:500] + "...")

        if self.cfg.get("dry_run"):
            return "Dry run enabled. No changes made."

        ans = input("Apply this AI patch? (y/N): ").strip().lower()
        if ans != 'y': return "Patch rejected."

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tf:
            tf.write(patch_text)
            tf.flush()
            try:
                subprocess.run(["git", "apply", tf.name], check=True)
                self.log_action(f"Applied patch to {file_path}")
                return "Patch applied successfully."
            except Exception as e:
                return f"Patch failed: {e}"

    # --- SYSTEM ACTIONS ---
    def execute(self, cmd):
        try:
            print(f"\033[1;33m[Executing]: {cmd}\033[1;m")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return str(e)

    def log_action(self, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {action}\n")

    # --- NATURAL LANGUAGE INTERFACE ---
    def process_natural_language(self, user_input):
        user_input = user_input.lower()
        
        # Self-Repair/Analyze Mode
        if "analyze" in user_input or "fix" in user_input:
            target = self.cfg.get("watch_path", ".")
            return self.run_self_analysis(target)

        # Standard Katoolin Logic
        if "setup" in user_input:
            return "Setting up repos..." # Add your setup logic here
        
        if "install" in user_input:
            words = user_input.split()
            tool = words[words.index("install") + 1] if "install" in words else "unknown"
            return f"Installing {tool}..." # Add your install logic here

        return "Commands: 'analyze', 'fix code', 'install [tool]', 'setup repos'"

    def run_self_analysis(self, path):
        """Runs flake8/checks and asks LLM for fixes (Integrated Analyzer)"""
        print(f"Scanning {path} for issues...")
        # Simple flake8 check
        result = self.execute(f"flake8 {path}")
        if not result:
            return "No issues found by analyzer."
        
        # Build prompt for the first issue found
        prompt = f"Fix the following error in a unified diff format:\n{result}"
        suggestion = self.get_llm_fix(prompt)
        
        if suggestion:
            return self.apply_patch(suggestion, path)
        return "LLM could not find a fix."

if __name__ == "__main__":
    assistant = LivingKatoolin()
    print("\033[1;32mLiving Katoolin + AI Agent Online.\033[1;m")
    
    while True:
        query = input("\033[1;36m[Living-AI] > \033[1;m")
        if query.lower() in ["exit", "quit"]: break
        print(assistant.process_natural_language(query))
