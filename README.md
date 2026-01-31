System Hardening


# Linux System Hardening

## Kernel Security
- Enable ASLR: echo 2 > /proc/sys/kernel/randomize_va_space
- Restrict kernel pointers: kernel.kptr_restrict=2
- Enable ExecShield protection
- Disable unused kernel modules

## File System Security
- Set proper permissions (umask 027)
- Enable disk encryption (LUKS)
- Mount options: noexec, nosuid, nodev for /tmp
- Implement file integrity monitoring (AIDE, Tripwire)

## Network Hardening
- Disable unnecessary services
- Configure iptables/nftables
- Enable TCP SYN cookies
- Disable ICMP redirects

## Access Control
- Implement least privilege principle
- Use sudo instead of direct root
- Configure PAM properly
- Set account lockout policies
Examples:
chmod 600 /etc/shadowsysctl -w net.ipv4.tcp_syncookies=1systemctl disable unused-service
Firewall Configuration


# Linux Firewall (iptables/nftables)

## iptables Basics
- INPUT: incoming traffic
- OUTPUT: outgoing traffic
- FORWARD: routed traffic

## Essential Rules
```bash
# Default deny policy
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow SSH (with rate limiting)
iptables -A INPUT -p tcp --dport 22 -m limit --limit 3/min -j ACCEPT
```

## nftables Modern Approach
```bash
nft add table inet filter
nft add chain inet filter input { type filter hook input priority 0 \; policy drop \; }
nft add rule inet filter input ct state established,related accept
```
Examples:
iptables -L -n -vnft list rulesetufw enable && ufw default deny incoming
SELinux Security


# SELinux (Security-Enhanced Linux)

## Modes
- Enforcing: Policies are enforced
- Permissive: Policies logged but not enforced
- Disabled: SELinux turned off

## Essential Commands
```bash
# Check status
getenforce
sestatus

# Set mode temporarily
setenforce 1  # Enforcing
setenforce 0  # Permissive

# Check file context
ls -Z /path/to/file

# Restore default context
restorecon -Rv /path

# Manage booleans
getsebool -a
setsebool -P httpd_can_network_connect on

# Troubleshoot
ausearch -m AVC -ts recent
audit2why < /var/log/audit/audit.log
```

## Custom Policies
- Use audit2allow to generate policies
- Test in permissive mode first
- Document all policy changes
Examples:
semanage fcontext -a -t httpd_sys_content_t "/web(/.*)?"audit2allow -M mypolicy < /var/log/audit/audit.log
Security Auditing


# Linux Security Auditing

## auditd Configuration
```bash
# Install
apt install auditd audispd-plugins

# Key audit rules
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/sudoers -p wa -k sudoers
-a always,exit -F arch=b64 -S execve -k exec
-a always,exit -F arch=b64 -S chmod,fchmod -k perm_mod
```

## Log Analysis
- ausearch: Search audit logs
- aureport: Generate reports
- aulast: Similar to last command

## Compliance Tools
- Lynis: Security auditing tool
- OpenSCAP: Compliance checking
- CIS Benchmarks: Industry standards

```bash
# Run Lynis audit
lynis audit system

# OpenSCAP scan
oscap xccdf eval --profile xccdf_org.ssgproject.content_profile_cis
```
Examples:
ausearch -k identity -ts todayaureport --summarylynis audit system --quick
Best Practices

Always follow the principle of least privilege
Keep systems updated with security patches
Use strong, unique passwords and implement MFA where possible
Monitor and audit system logs regularly
Implement defense in depth with multiple security layers
Document all security configurations and changes
Regularly test security controls and incident response
Encrypt sensitive data at rest and in transit
Command Reference

iptables
caution
Configure IPv4 packet filtering and NAT
iptables [-t table] {-A|-C|-D} chain rule-specification
auditctl
safe
Configure the audit system
auditctl [options]


#!/usr/bin/env python3
"""
Automated Reconnaissance Scanner
Gathers information about target domains
"""

import socket
import subprocess
import json
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor

class ReconScanner:
    def __init__(self, target: str):
        self.target = target
        self.results: Dict = {}
        
    def dns_lookup(self) -> Dict:
        """Perform DNS lookups"""
        records = {}
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']
        
        for rtype in record_types:
            try:
                result = subprocess.run(
                    ['dig', '+short', rtype, self.target],
                    capture_output=True, text=True, timeout=10
                )
                if result.stdout.strip():
                    records[rtype] = result.stdout.strip().split('\n')
            except:
                pass
                
        self.results['dns'] = records
        return records
        
    def port_scan(self, ports: List[int] = None) -> Dict:
        """Basic port scanning"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
                    993, 995, 3306, 3389, 5432, 8080, 8443]
        
        open_ports = []
        
        def check_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.target, port))
                sock.close()
                return port if result == 0 else None
            except:
                return None
                
        with ThreadPoolExecutor(max_workers=20) as executor:
            results = executor.map(check_port, ports)
            open_ports = [p for p in results if p]
            
        self.results['open_ports'] = open_ports
        return {'open_ports': open_ports}
        
    def whois_lookup(self) -> str:
        """Perform WHOIS lookup"""
        try:
            result = subprocess.run(
                ['whois', self.target],
                capture_output=True, text=True, timeout=30
            )
            self.results['whois'] = result.stdout
            return result.stdout
        except:
            return ""
            
    def run_full_scan(self) -> Dict:
        """Run complete reconnaissance"""
        print(f"[*] Starting recon on {self.target}")
        
        print("[+] DNS lookup...")
        self.dns_lookup()
        
        print("[+] Port scanning...")
        self.port_scan()
        
        print("[+] WHOIS lookup...")
        self.whois_lookup()
        
        print("[+] Scan complete!")
        return self.results

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: recon-scanner.py <target>")
        sys.exit(1)
    
    scanner = ReconScanner(sys.argv[1])
    results = scanner.run_full_scan()
    print(json.dumps(results, indent=2))
#!/usr/bin/env python3
"""
Linux Security Scanner
Checks for common security misconfigurations
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

class SecurityScanner:
    def __init__(self):
        self.results = []
        self.score = 100
        
    def log(self, level: str, check: str, message: str, deduction: int = 0):
        self.results.append({
            "level": level,
            "check": check,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        if level in ["FAIL", "WARN"]:
            self.score -= deduction
            
    def check_permissions(self):
        """Check critical file permissions"""
        critical_files = {
            "/etc/passwd": "644",
            "/etc/shadow": "600",
            "/etc/group": "644",
            "/etc/gshadow": "600",
            "/etc/sudoers": "440",
        }
        
        for file, expected in critical_files.items():
            if os.path.exists(file):
                actual = oct(os.stat(file).st_mode)[-3:]
                if actual == expected:
                    self.log("PASS", f"permissions:{file}", f"Correct permissions {actual}")
                else:
                    self.log("FAIL", f"permissions:{file}", 
                            f"Expected {expected}, got {actual}", 5)
            else:
                self.log("WARN", f"permissions:{file}", "File not found", 2)
                
    def check_sshd(self):
        """Check SSH configuration"""
        sshd_config = "/etc/ssh/sshd_config"
        if not os.path.exists(sshd_config):
            self.log("WARN", "sshd:config", "SSHD config not found", 5)
            return
            
        with open(sshd_config) as f:
            config = f.read()
            
        checks = [
            ("PermitRootLogin no", "Root login should be disabled"),
            ("PasswordAuthentication no", "Password auth should be disabled"),
            ("X11Forwarding no", "X11 forwarding should be disabled"),
        ]
        
        for check, message in checks:
            if check.split()[0] in config:
                if check in config:
                    self.log("PASS", f"sshd:{check.split()[0]}", message)
                else:
                    self.log("FAIL", f"sshd:{check.split()[0]}", message, 5)
                    
    def check_kernel_params(self):
        """Check kernel security parameters"""
        params = {
            "kernel.randomize_va_space": "2",
            "net.ipv4.tcp_syncookies": "1",
            "net.ipv4.conf.all.accept_redirects": "0",
        }
        
        for param, expected in params.items():
            try:
                result = subprocess.run(
                    ["sysctl", "-n", param],
                    capture_output=True, text=True
                )
                actual = result.stdout.strip()
                if actual == expected:
                    self.log("PASS", f"kernel:{param}", f"Value is {actual}")
                else:
                    self.log("FAIL", f"kernel:{param}", 
                            f"Expected {expected}, got {actual}", 3)
            except Exception as e:
                self.log("WARN", f"kernel:{param}", str(e), 2)
                
    def check_services(self):
        """Check for unnecessary services"""
        dangerous_services = [
            "telnet", "rsh", "rlogin", "tftp", "vsftpd"
        ]
        
        for service in dangerous_services:
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    capture_output=True, text=True
                )
                if result.stdout.strip() == "active":
                    self.log("FAIL", f"service:{service}", 
                            f"Dangerous service {service} is running", 10)
                else:
                    self.log("PASS", f"service:{service}", 
                            f"Service {service} is not running")
            except:
                pass
                
    def run(self):
        """Run all security checks"""
        print("Starting security scan...")
        self.check_permissions()
        self.check_sshd()
        self.check_kernel_params()
        self.check_services()
        
        print(f"\nSecurity Score: {max(0, self.score)}/100")
        print(f"\nResults:")
        for r in self.results:
            status = "✓" if r["level"] == "PASS" else "✗" if r["level"] == "FAIL" else "!"
            print(f"  [{status}] {r['check']}: {r['message']}")
            
        return self.results

if __name__ == "__main__":
    scanner = SecurityScanner()
    scanner.run()

    #!/bin/bash
# Firewall Configuration Manager

set -euo pipefail

IPTABLES=$(command -v iptables || echo "")
NFT=$(command -v nft || echo "")

apply_iptables() {
    echo "Configuring iptables..."
    
    # Flush existing rules
    iptables -F
    iptables -X
    iptables -t nat -F
    iptables -t mangle -F
    
    # Default policies
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT
    
    # Allow loopback
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT
    
    # Allow established connections
    iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
    
    # SSH with rate limiting
    iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -m limit --limit 3/min --limit-burst 3 -j ACCEPT
    
    # HTTP/HTTPS (optional)
    # iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    # iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    
    # Log dropped packets
    iptables -A INPUT -j LOG --log-prefix "DROPPED: " --log-level 4
    
    echo "iptables configured successfully"
}

apply_nftables() {
    echo "Configuring nftables..."
    
    nft flush ruleset
    
    nft add table inet filter
    nft add chain inet filter input '{ type filter hook input priority 0; policy drop; }'
    nft add chain inet filter forward '{ type filter hook forward priority 0; policy drop; }'
    nft add chain inet filter output '{ type filter hook output priority 0; policy accept; }'
    
    # Allow loopback
    nft add rule inet filter input iif lo accept
    
    # Allow established
    nft add rule inet filter input ct state established,related accept
    
    # SSH with rate limiting
    nft add rule inet filter input tcp dport 22 ct state new limit rate 3/minute accept
    
    echo "nftables configured successfully"
}

# Main
if [[ -n "$NFT" ]]; then
    apply_nftables
elif [[ -n "$IPTABLES" ]]; then
    apply_iptables
else
    echo "No firewall tool found!"
    exit 1
fi



    
