#!/usr/bin/env python3
import json
import sys

from session_context import handoff_path, project_root, read_input, status


data = read_input()
root = project_root(data)
is_antigravity = "--host" in sys.argv and "antigravity" in sys.argv
if "workspacePaths" in data or "modelName" in data:
    is_antigravity = True

if root is None:
    if is_antigravity:
        print(json.dumps({}))
    sys.exit(0)

output_lines = ["Session status (from git):\n" + status(root)]
model = data.get("modelName") or data.get("model")
if isinstance(model, str):
    output_lines.append("- Active model: " + model)
path = handoff_path(root)
try:
    with path.open(encoding="utf-8", errors="replace") as stream:
        text = stream.read(6001).strip()
except OSError:
    text = ""
if text:
    if len(text) > 6000:
        text = text[:6000] + "\n...(truncated; keep handoff.md under 40 lines)"
    output_lines.append(f"\nPrevious task state from {path.relative_to(root)} (verify against the current request and files):\n{text}")

full_text = "\n".join(output_lines)
if is_antigravity:
    print(json.dumps({
        "injectSteps": [
            {
                "systemMessage": {
                    "systemMessage": full_text
                }
            }
        ]
    }))
else:
    print(full_text)
