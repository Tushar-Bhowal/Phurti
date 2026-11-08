#!/usr/bin/env python3
import argparse
import json
import sys

from session_context import handoff_path, ignore_scratch, project_root, read_input, status


parser = argparse.ArgumentParser()
parser.add_argument("--host", choices=("claude", "codex"), default="claude")
args = parser.parse_args()
data = read_input()
root = project_root(data)
if root is None:
    sys.exit(0)
path = handoff_path(root)
if not path.is_file() and ignore_scratch(root):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as stream:
            stream.write("# Handoff\n\nNo narrative checkpoint was saved. Git state at compaction:\n\n")
            stream.write(status(root) + "\n")
    except OSError:
        pass
message = (
    "Phurti preserved the existing handoff or captured git state; SessionStart reloads it after compaction."
    if path.is_file() else "Phurti could not save a compaction checkpoint."
)
if args.host == "codex":
    print(json.dumps({"systemMessage": message}))
else:
    print(message)
