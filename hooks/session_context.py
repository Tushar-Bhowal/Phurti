import json
import os
from pathlib import Path
import subprocess
import sys


def read_input():
    try:
        data = json.load(sys.stdin)
        return data if isinstance(data, dict) else {}
    except (ValueError, OSError):
        return {}


def git(cwd, *args):
    try:
        result = subprocess.run(
            ["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=3,
        )
        return result.stdout.rstrip() if result.returncode == 0 else ""
    except (OSError, subprocess.TimeoutExpired):
        return ""


def project_root(data):
    cwd = data.get("cwd") or os.getcwd()
    root = git(cwd, "rev-parse", "--show-toplevel")
    return Path(root) if root else None


def handoff_path(root):
    shared = root / ".phurti/handoff.md"
    legacy = root / ".claude/handoff.md"
    return shared if shared.is_file() or not legacy.is_file() else legacy


def ignore_scratch(root):
    if git(root, "check-ignore", ".phurti/handoff.md"):
        return True
    location = git(root, "rev-parse", "--git-path", "info/exclude")
    if not location:
        return False
    path = root / location
    try:
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(("\n" if existing and not existing.endswith("\n") else "") + "/.phurti/\n")
        return True
    except (OSError, UnicodeError):
        return False


def status(root):
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD") or "(unborn or detached)"
    last = git(root, "log", "-1", "--pretty=%h %s")
    changes = git(root, "status", "--porcelain").splitlines()
    lines = [f"- Branch: {branch}"]
    if last:
        lines.append(f"- Last commit: {last}")
    lines.append(f"- Uncommitted changes: {len(changes)} file(s)" if changes else "- Working tree clean")
    lines.extend("  " + line for line in changes[:5])
    return "\n".join(lines)
