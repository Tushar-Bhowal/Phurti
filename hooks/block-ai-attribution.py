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

if not isinstance(data, dict) or data.get("tool_name") != "Bash":
    sys.exit(0)

tool_input = data.get("tool_input", {}) or {}
if not isinstance(tool_input, dict):
    sys.exit(0)
cmd = tool_input.get("command", "") or ""
if not isinstance(cmd, str):
    sys.exit(0)

# Only inspect git commit commands.
if not re.search(r"\bgit\b.*\bcommit\b", cmd, re.IGNORECASE | re.DOTALL):
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
        sys.stderr.write(
            "Blocked: the commit message contains AI/model attribution "
            f"(matched: '{pat}'). Rewrite it as a human engineer would — no "
            "tool attribution or co-author trailer; no 'Generated "
            "with' footer; no Co-Authored-By trailer. Then commit again.\n"
        )
        sys.exit(2)

sys.exit(0)
