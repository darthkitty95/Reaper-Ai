import os
import subprocess
import importlib.util
from git import Repo

class SelfEvolver:
    def __init__(self, tool_dir="./dynamic_tools"):
        self.tool_dir = tool_dir
        os.makedirs(self.tool_dir, exist_ok=True)

    def download_tool(self, repo_url):
        """Clones a new tool from GitHub into the dynamic tools folder."""
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        target_path = os.path.join(self.tool_dir, repo_name)
        
        if not os.path.exists(target_path):
            print(f"[*] Evolution: Downloading new capability from {repo_url}...")
            Repo.clone_from(repo_url, target_path)
            # Automatically install requirements if they exist
            req_path = os.path.join(target_path, "requirements.txt")
            if os.path.exists(req_path):
                subprocess.run(["pip", "install", "-r", req_path], capture_output=True)
            return target_path
        return target_path

    def integrate_module(self, module_path, module_name):
        """Dynamically loads a Python file as a module."""
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        new_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(new_module)
        return new_module

# --- Example Autonomous Flow ---
# 1. Gemini decides it needs 'sqlmap' style logic.
# 2. Evolver downloads a specialized repo.
# 3. Evolver integrates and the script immediately uses 'new_module.run_exploit()'.
