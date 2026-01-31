import subprocess
import tempfile
from pathlib import Path
from git import Repo

class Patcher:
    def __init__(self, repo_root: Path, cfg: dict, knowledge):
        self.repo_root = repo_root
        self.cfg = cfg
        self.knowledge = knowledge
        self.repo = Repo(self.repo_root)

    def present_patch(self, patch_text: str, diagnostic):
        print(f"[patcher] suggested patch for {diagnostic.file_path}:\n{patch_text[:2000]}")
        
        if self.cfg.get("dry_run", True):
            print("[patcher] dry_run mode: skipping application.")
            return

        if self.cfg.get("require_approval", True):
            if input("Apply patch? (y/N): ").lower() != "y":
                return

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tf:
            tf.write(patch_text)
            tf_path = tf.name

        try:
            subprocess.check_output(["git", "apply", tf_path], cwd=self.repo_root)
            self.repo.index.add(all=True)
            self.repo.index.commit(f"AI-agent: fix {Path(diagnostic.file_path).name}")
            print("[patcher] Applied and committed.")
            self.knowledge.add_example(diagnostic, patch_text)
        except Exception as e:
            print(f"[patcher] application failed: {e}")
import base64

def obfuscate_asset(code_text):
    # Simple XOR obfuscation with a key
    key = "stealth_key"
    xor_output = "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(code_text))
    return base64.b64encode(xor_output.encode()).decode()

def deobfuscate_for_execution(obfuscated_text):
    # Deobfuscates right before the interpreter runs it
    key = "stealth_key"
    decoded = base64.b64decode(obfuscated_text).decode()
    return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(decoded))

