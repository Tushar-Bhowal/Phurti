#!/usr/bin/env python3
import sys

from session_context import handoff_path, project_root, read_input, status


data = read_input()
root = project_root(data)
if root is None:
    sys.exit(0)
print("Session status (from git):\n" + status(root))
if isinstance(data.get("model"), str):
    print("- Active model: " + data["model"])
path = handoff_path(root)
try:
    with path.open(encoding="utf-8", errors="replace") as stream:
        text = stream.read(6001).strip()
except OSError:
    text = ""
if text:
    if len(text) > 6000:
        text = text[:6000] + "\n...(truncated; keep handoff.md under 40 lines)"
    print(f"\nPrevious task state from {path.relative_to(root)} (verify against the current request and files):\n{text}")
