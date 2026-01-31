#!/usr/bin/python3
"""
Aegis-Nexus: Unified AI-Driven Ethical Hacking & Hardening Suite
Integrates: Living Katoolin, System Hardener, and Offensive Recon
"""

import os
import sys
import json
import subprocess
import sqlite3
import hashlib
import tempfile
import asyncio
import aiohttp
import nmap3
import yaml
from datetime import datetime
from pathlib import Path

# Required: pip install GitPython PyYAML openai python-nmap3 aiohttp
try:
    from git import Repo
    import openai
except ImportError:
    print("[!] Missing dependencies. Run: pip install GitPython PyYAML openai python-nmap3 aiohttp")

class AegisNexus:
    def __init__(self, target="127.0.0.1", config_path="config.yaml"):
        self.target = target
        self.config_path = Path(config_path)
        self.log_file = "aegis_nexus.log"
        
        # Load Configuration
        self.cfg = self._load_config()
        
        # Unified Memory (Red/Blue/AI)
        self.memory = {
            "installed_tools": [],
            "hardening_applied": False,
            "last_recon": {},
            "repo_added": False
        }
        self._load_memory()
        
        # Database for AI Patches
        self.db_path = Path(self.cfg.get("knowledge_db", "./agent_data/knowledge.db"))
        self._ensure_db_table()
        
        if self.cfg.get("llm_provider") == "openai":
            openai.api_key = os.getenv("OPENAI_API_KEY")

    # --- CORE UTILITIES ---
    def _load_config(self):
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f)
        return {"llm_provider": "openai", "llm_model": "gpt-4o-mini", "dry_run": False}

    def _load_memory(self):
        if os.path.exists("brain.json"):
            with open("brain.json", "r") as f:
                self.memory.update(json.load(f))

    def _save_memory(self):
        with open("brain.json", "w") as f:
            json.dump(self.memory, f, indent=4)

    def _ensure_db_table(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("CREATE TABLE IF NOT EXISTS examples (id TEXT PRIMARY KEY, diagnostic TEXT, patch TEXT, metadata TEXT)")
        conn.commit()
        conn.close()

    def log(self, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{ts}] {msg}\n")
        print(f"[*] {msg}")

    # --- BLUE TEAM: SYSTEM HARDENING ---
    def harden_system(self):
        if os.getuid() != 0:
            return "Root required for hardening."
        
        self.log("Applying Kernel Hardening...")
        params = {
            "kernel.randomize_va_space": "2",
            "net.ipv4.tcp_syncookies": "1",
            "kernel.kptr_restrict": "2"
        }
        for p, v in params.items():
            subprocess.run(["sysctl", "-w", f"{p}={v}"], capture_output=True)
            
        self.log("Configuring nftables Default-Deny...")
        fw_cmds = [
            "nft flush ruleset",
            "nft add table inet filter",
            "nft add chain inet filter input { type filter hook input priority 0 ; policy drop ; }",
            "nft add rule inet filter input ct state established,related accept"
        ]
        for cmd in fw_cmds:
            subprocess.run(cmd, shell=True)
        
        self.memory["hardening_applied"] = True
        self._save_memory()
        return "System Hardened."

    # --- RED TEAM: OFFENSIVE RECON ---
    async def run_recon(self):
        self.log(f"Starting Recon on {self.target}...")
        nmap = nmap3.NmapHostDiscovery()
        results = nmap.nmap_portscan_only(self.target)
        
        # Check for Web Vulnerabilities
        async with aiohttp.ClientSession() as session:
            for path in ["/.env", "/api/v1/debug?cmd=id"]:
                try:
                    async with session.get(f"http://{self.target}{path}", timeout=2) as resp:
                        if resp.status == 200:
                            self.log(f"ALERT: Exposed path found: {path}")
                except: continue
        
        self.memory["last_recon"] = results
        self._save_memory()
        return "Recon Complete."

    # --- AI AGENT: SELF-REPAIR & PATCHING ---
    def get_ai_fix(self, error_report):
        prompt = f"Fix this code error in unified diff format:\n{error_report}"
        try:
            resp = openai.ChatCompletion.create(
                model=self.cfg.get("llm_model"),
                messages=[{"role": "user", "content": prompt}]
            )
            return resp["choices"][0]["message"]["content"]
        except Exception as e:
            return f"AI Error: {e}"

    def apply_patch(self, patch_text):
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tf:
            tf.write(patch_text)
            tf.flush()
            subprocess.run(["git", "apply", tf.name])
        return "Patch Applied."

    # --- INTERFACE ---
    async def process_cmd(self, cmd):
        cmd = cmd.lower()
        if "harden" in cmd: return self.harden_system()
        if "recon" in cmd: return await self.run_recon()
        if "analyze" in cmd:
            issue = subprocess.run(["flake8", "."], capture_output=True, text=True).stdout
            if not issue: return "No local code issues."
            fix = self.get_ai_fix(issue)
            return self.apply_patch(fix)
        if "install" in cmd:
            tool = cmd.split("install ")[-1]
            subprocess.run(["apt", "install", "-y", tool])
            self.memory["installed_tools"].append(tool)
            self._save_memory()
            return f"Installed {tool}."
        
        return "Commands: harden, recon, analyze, install [tool], exit"

async def main_loop():
    nexus = AegisNexus()
    print("\033[1;32m[Aegis-Nexus] Unified AI Security Suite Online.\033[0m")
    while True:
        try:
            query = input("\033[1;36mNexus > \033[0m")
            if query.lower() in ["exit", "quit"]: break
            response = await nexus.process_cmd(query)
            print(f"[-] {response}")
        except KeyboardInterrupt: break

if __name__ == "__main__":
    asyncio.run(main_loop())
