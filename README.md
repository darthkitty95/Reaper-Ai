import os
import subprocess
import json
import asyncio
import socket
import aiohttp
import nmap3
from datetime import datetime
from pathlib import Path

class AegisNexus:
    def __init__(self, target_ip="127.0.0.1"):
        self.target = target_ip
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.report = {
            "meta": {"target": self.target, "start_time": self.timestamp},
            "defense": {"hardening_actions": [], "local_vulnerabilities": []},
            "offense": {"recon_data": {}, "remote_vulnerabilities": []}
        }

    # ==========================================
    # 🔵 BLUE TEAM: LOCAL SYSTEM HARDENING
    # ==========================================
    
    def apply_hardening(self):
        """Applies Kernel and Firewall rules (Requires Root)"""
        print("\n[🛡️] Phase 1: Local Hardening...")
        
        # Kernel Hardening
        params = {
            "kernel.randomize_va_space": "2",
            "net.ipv4.tcp_syncookies": "1",
            "net.ipv4.conf.all.accept_redirects": "0",
            "kernel.kptr_restrict": "2"
        }
        for param, value in params.items():
            subprocess.run(["sysctl", "-w", f"{param}={value}"], capture_output=True)
            self.report["defense"]["hardening_actions"].append(f"Hardened {param}")

        # Firewall (nftables)
        fw_cmds = [
            "nft flush ruleset",
            "nft add table inet filter",
            "nft add chain inet filter input { type filter hook input priority 0 ; policy drop ; }",
            "nft add rule inet filter input ct state established,related accept",
            "nft add rule inet filter input tcp dport 22 limit rate 3/minute accept"
        ]
        for cmd in fw_cmds:
            subprocess.run(cmd, shell=True, capture_output=True)
        self.report["defense"]["hardening_actions"].append("Firewall: Default Deny + SSH Rate Limit")

    async def audit_local_system(self):
        """Checks for local misconfigurations"""
        print("[🔍] Phase 2: Local Audit...")
        
        # SELinux Check
        try:
            status = subprocess.check_output(["getenforce"], text=True).strip()
            if status != "Enforcing":
                self.report["defense"]["local_vulnerabilities"].append(f"SELinux is {status}")
        except FileNotFoundError:
            self.report["defense"]["local_vulnerabilities"].append("SELinux not installed")

        # Port Check (Internal)
        proc = subprocess.run(["ss", "-tuln"], capture_output=True, text=True)
        if ":21 " in proc.stdout:
            self.report["defense"]["local_vulnerabilities"].append("FTP (21) is exposed locally!")

    # ==========================================
    # 🔴 RED TEAM: EXTERNAL RECON & ATTACK
    # ==========================================

    async def run_external_recon(self):
        """Modern Nmap scanning"""
        print(f"\n[🚀] Phase 3: External Recon on {self.target}...")
        nmap = nmap3.NmapHostDiscovery()
        try:
            self.report["offense"]["recon_data"] = nmap.nmap_portscan_only(self.target)
        except Exception as e:
            print(f"[-] Nmap failed: {e}")

    async def check_remote_vulns(self):
        """Asynchronous Web Vulnerability Probing"""
        print("[💥] Phase 4: Remote Vulnerability Check...")
        async with aiohttp.ClientSession() as session:
            # Paths inspired by your roadmap and CVE-2026 templates
            paths = ["/.env", "/.git/config", "/api/v1/debug?cmd=id"]
            for path in paths:
                url = f"http://{self.target}{path}"
                try:
                    async with session.get(url, timeout=3) as resp:
                        content = await resp.text()
                        if resp.status == 200:
                            status = "EXPOSED"
                            if "uid=" in content or "groups=" in content:
                                status = "VULNERABLE (RCE Detected)"
                            self.report["offense"]["remote_vulnerabilities"].append({"url": url, "status": status})
                except:
                    continue

    # ==========================================
    # 📑 INTEGRATION: REPORTING
    # ==========================================

    def save_nexus_report(self):
        filename = f"nexus_report_{self.timestamp}.json"
        with open(filename, "w") as f:
            json.dump(self.report, f, indent=4)
        print(f"\n[!] Unified Security Report saved to: {filename}")

# --- EXECUTION ENGINE ---
async def main():
    # Prompt for target
    target = input("Enter target IP/Domain for Recon (default: 127.0.0.1): ") or "127.0.0.1"
    nexus = AegisNexus(target)

    # 1. Defense first (requires sudo)
    if os.getuid() == 0:
        nexus.apply_hardening()
    else:
        print("[!] Not running as root. Skipping Firewall/Kernel hardening.")

    # 2. Run Local Audit and External Recon concurrently
    await asyncio.gather(
        nexus.audit_local_system(),
        nexus.run_external_recon(),
        nexus.check_remote_vulns()
    )

    # 3. Finalize
    nexus.save_nexus_report()

if __name__ == "__main__":
    asyncio.run(main())

    import os
import subprocess
import json
import asyncio
import aiohttp
import nmap3
from datetime import datetime

class IntegratedSecuritySuite:
    def __init__(self, target="127.0.0.1"):
        self.target = target
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "hardening": [],
            "recon_results": {},
            "vulnerabilities": []
        }

    # === BLUE TEAM: HARDENING & FIREWALL ===
    def apply_defense(self):
        """Integrates Kernel Hardening and Firewall Rules"""
        if os.getuid() != 0:
            print("[!] Skipping Hardening: Root privileges required.")
            return

        print("[*] Applying Kernel Security & Firewall...")
        # Kernel Logic
        params = {"kernel.randomize_va_space": "2", "net.ipv4.tcp_syncookies": "1"}
        for p, v in params.items():
            subprocess.run(["sysctl", "-w", f"{p}={v}"], capture_output=True)
        
        # Firewall Logic (nftables)
        fw_script = [
            "nft flush ruleset",
            "nft add table inet filter",
            "nft add chain inet filter input { type filter hook input priority 0 ; policy drop ; }",
            "nft add rule inet filter input ct state established,related accept"
        ]
        for cmd in fw_script:
            subprocess.run(cmd, shell=True)
        self.report["hardening"].append("Kernel hardened and Firewall set to Default Deny.")

    # === RED TEAM: RECON & VULN SCANNING ===
    async def run_offensive_suite(self):
        """Integrates Nmap Recon and Web Vulnerability Probing"""
        print(f"[*] Starting Recon/Attack Phase on {self.target}...")
        
        # 1. Nmap Recon
        nmap = nmap3.NmapHostDiscovery()
        try:
            self.report["recon_results"] = nmap.nmap_portscan_only(self.target)
        except:
            print("[-] Nmap scan failed. Ensure nmap is installed.")

        # 2. Web Vulnerability (The "Modern CVE" Logic)
        async with aiohttp.ClientSession() as session:
            paths = ["/.env", "/api/v1/debug?cmd=id"]
            for path in paths:
                try:
                    async with session.get(f"http://{self.target}{path}", timeout=2) as resp:
                        if resp.status == 200:
                            body = await resp.text()
                            status = "EXPOSED"
                            if "uid=" in body: status = "CRITICAL: RCE VULNERABILITY"
                            self.report["vulnerabilities"].append({"path": path, "result": status})
                except: continue

    # === REPORTING ===
    def finalize(self):
        filename = f"security_log_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(self.report, f, indent=4)
        print(f"\n[+] Suite Execution Finished. Report saved to {filename}")

# --- MAIN EXECUTION ---
async def main():
    suite = IntegratedSecuritySuite(target="127.0.0.1") # Set your target here
    
    # 1. Harden the system (Blue)
    suite.apply_defense()
    
    # 2. Run offensive tools (Red)
    await suite.run_offensive_suite()
    
    # 3. Save everything
    suite.finalize()

if __name__ == "__main__":
    asyncio.run(main())

