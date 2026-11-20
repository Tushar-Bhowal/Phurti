#!/usr/bin/env python3
import json
import re
import sys
import os
import shlex

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # can't parse -> never block on uncertainty

if not isinstance(data, dict):
    sys.exit(0)

is_antigravity = "--host" in sys.argv and "antigravity" in sys.argv
if "toolCall" in data or "workspacePaths" in data:
    is_antigravity = True

tool_call = data.get("toolCall") if isinstance(data.get("toolCall"), dict) else {}
tool_name = data.get("tool_name") or tool_call.get("name", "")

if tool_name not in ("Bash", "run_command"):
    if is_antigravity:
        print(json.dumps({"decision": "allow"}))
    sys.exit(0)

tool_input = data.get("tool_input") if isinstance(data.get("tool_input"), dict) else {}
tool_call_args = tool_call.get("args") if isinstance(tool_call.get("args"), dict) else {}
cmd = tool_input.get("command") or tool_call_args.get("CommandLine") or ""
if not isinstance(cmd, str):
    if is_antigravity:
        print(json.dumps({"decision": "allow"}))
    sys.exit(0)

# Only inspect git commit commands.
if not re.search(r"\bgit\b.*\bcommit\b", cmd, re.IGNORECASE | re.DOTALL):
    if is_antigravity:
        print(json.dumps({"decision": "allow"}))
    sys.exit(0)

PATTERNS = [
    r"generated (?:with|by)",
    r"co-?authored-?by:",
    r"noreply@(?:anthropic|openai)\.com",
    r"🤖",
    r"(?:written|implemented|assisted|powered) by (?:claude|codex|chatgpt|openai|an? ai)",
    r"(?:with|using) (?:claude code|codex|chatgpt)",
    r"ai[-\s]generated",
]

text = cmd
try:
    lexer = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    tokens = list(lexer)
except ValueError:
    tokens = []
cwd = data.get("cwd") or os.getcwd()
commit = False
index = 0
while index < len(tokens):
    token = tokens[index]
    if token in (";", "&&", "||", "|"):
        commit = False
        cwd = data.get("cwd") or os.getcwd()
    elif os.path.basename(token) == "git":
        commit = False
        cwd = data.get("cwd") or os.getcwd()
    elif not commit and token == "-C" and index + 1 < len(tokens):
        index += 1
        cwd = os.path.join(cwd, tokens[index])
    elif not commit and token.startswith("-C") and len(token) > 2:
        cwd = os.path.join(cwd, token[2:])
    elif token == "commit":
        commit = True
    elif commit:
        message_file = None
        if token in ("-F", "--file") and index + 1 < len(tokens):
            index += 1
            message_file = tokens[index]
        elif token.startswith("--file="):
            message_file = token.split("=", 1)[1]
        elif token.startswith("-F") and len(token) > 2:
            message_file = token[2:]
        if message_file and message_file != "-":
            try:
                with open(os.path.join(cwd, message_file), encoding="utf-8") as stream:
                    text += "\n" + stream.read()
            except (OSError, UnicodeError):
                pass
    index += 1

for pat in PATTERNS:
    if re.search(pat, text, re.IGNORECASE):
        msg = (
            "Blocked: the commit message contains AI/model attribution "
            f"(matched: '{pat}'). Rewrite it as a human engineer would — no "
            "tool attribution or co-author trailer; no 'Generated "
            "with' footer; no Co-Authored-By trailer. Then commit again."
        )
        if is_antigravity:
            print(json.dumps({"decision": "deny", "reason": msg}))
            sys.exit(0)
        sys.stderr.write(msg + "\n")
        sys.exit(2)

if is_antigravity:
    print(json.dumps({"decision": "allow"}))
sys.exit(0)
