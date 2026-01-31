This is a comprehensive README.md designed to act as the "Master Control" for your integrated script. It combines the Hacker Roadmap philosophy, your Python Living Script capabilities, and the System Hardening standards into one professional document.
🛡️ Aegis-Nexus: Unified Hardening & Offensive Suite
Aegis-Nexus is a "Living Script" framework designed to bridge the gap between Ethical Hacking (Red Team) and System Hardening (Blue Team). Inspired by the Hacker Roadmap, this suite automates reconnaissance while simultaneously locking down the host system's kernel and network layers.
🚀 Key Features
🔴 Red Team (Offensive)
• Asynchronous Recon: High-speed port scanning via python-nmap3.
• Web Vulnerability Probing: Scans for sensitive files (.env, .git) using aiohttp.
• Modern Exploit Matching: Built-in logic to detect Remote Code Execution (RCE) patterns (e.g., uid=0 detection).
🔵 Blue Team (Defensive)
• Kernel Hardening: Automatic injection of security parameters via sysctl (ASLR, SYN Cookies, ICMP Redirects).
• Firewall Orchestration: Instant deployment of nftables "Default Deny" policies.
• Security Auditing: Local audit of SELinux status and exposed internal services (FTP, Telnet).
📂 Project Structure
