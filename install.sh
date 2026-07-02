#!/usr/bin/env bash
# Installs Phurti. Claude Code gets the full kit (skills + review agents + hooks + rules).
# Codex gets the always-on ruleset via AGENTS.md. Copilot / Antigravity: see the notes printed
# at the end. Safe to re-run: copies files and merges settings without duplicating or clobbering.
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST="$HOME/.claude"

echo "Installing Phurti ..."

# Appends the marked rule block from AGENTS.md to a target file, idempotently.
append_rules() {  # $1 = target file
  python3 - "$SRC/AGENTS.md" "$1" << 'PYEOF'
import os, sys
src, target = sys.argv[1], os.path.expanduser(sys.argv[2])
lines = open(src).read().splitlines(keepends=True)
block, capture = [], False
for ln in lines:
    if ">>> phurti rules >>>" in ln: capture = True
    if capture: block.append(ln)
    if "<<< phurti rules <<<" in ln: break
block = "".join(block).strip() + "\n"
existing = open(target).read() if os.path.isfile(target) else ""
if ">>> phurti rules >>>" in existing:
    print(f"  rules already present in {target} - left as is")
else:
    os.makedirs(os.path.dirname(target), exist_ok=True)
    sep = "\n\n" if existing.strip() else ""
    with open(target, "a") as f: f.write(sep + block)
    print(f"  {'appended' if existing.strip() else 'created'} rules in {target}")
PYEOF
}

# ---- Claude Code (full kit) ----
mkdir -p "$DST/skills/phurti-feature" "$DST/skills/phurti-architect" "$DST/skills/phurti-fix" "$DST/skills/phurti-audit" "$DST/skills/phurti-memory" "$DST/hooks" "$DST/agents"
cp "$SRC/skills/phurti-feature/SKILL.md"       "$DST/skills/phurti-feature/SKILL.md"
cp "$SRC/skills/phurti-architect/SKILL.md"     "$DST/skills/phurti-architect/SKILL.md"
cp "$SRC/skills/phurti-fix/SKILL.md"           "$DST/skills/phurti-fix/SKILL.md"
cp "$SRC/skills/phurti-audit/SKILL.md"         "$DST/skills/phurti-audit/SKILL.md"
cp "$SRC/skills/phurti-memory/SKILL.md"  "$DST/skills/phurti-memory/SKILL.md"
cp "$SRC"/agents/*.md                   "$DST/agents/"
cp "$SRC/hooks/block-ai-attribution.py" "$DST/hooks/block-ai-attribution.py"
cp "$SRC/hooks/protect-tests.py"        "$DST/hooks/protect-tests.py"
cp "$SRC/hooks/session-status.py"       "$DST/hooks/session-status.py"
chmod +x "$DST"/hooks/*.py

echo "Claude Code:"
append_rules "~/.claude/CLAUDE.md"

# Merge hooks into ~/.claude/settings.json (idempotent, non-destructive)
python3 - << 'PYEOF'
import json, os
p = os.path.expanduser("~/.claude/settings.json")
s = {}
if os.path.isfile(p):
    try: s = json.load(open(p))
    except Exception: s = {}
pre = s.setdefault("hooks", {}).setdefault("PreToolUse", [])
def has(sub): return any(sub in h.get("command","") for e in pre for h in e.get("hooks",[]))
if not has("block-ai-attribution.py"):
    pre.append({"matcher":"Bash","hooks":[{"type":"command","command":"python3 ~/.claude/hooks/block-ai-attribution.py"}]})
if not has("protect-tests.py"):
    pre.append({"matcher":"Edit|MultiEdit|Write","hooks":[{"type":"command","command":"python3 ~/.claude/hooks/protect-tests.py"}]})
start = s["hooks"].setdefault("SessionStart", [])
if not any("session-status.py" in h.get("command","") for e in start for h in e.get("hooks",[])):
    start.append({"hooks":[{"type":"command","command":"python3 ~/.claude/hooks/session-status.py"}]})
# Make the agent ask before reading a secret file, even in auto-accept mode.
ask = s.setdefault("permissions", {}).setdefault("ask", [])
for rule in ["Read(./.env)", "Read(./.env.*)", "Bash(cat .env*)", "Bash(printenv*)", "Bash(env)"]:
    if rule not in ask:
        ask.append(rule)
json.dump(s, open(p,"w"), indent=2)
print("  merged hooks + .env access prompts into", p)
PYEOF

# ---- Codex CLI (always-on ruleset via AGENTS.md) ----
echo "Codex CLI:"
append_rules "~/.codex/AGENTS.md"

cat << 'NOTE'

Done.

Claude Code  - full kit: /phurti-architect  /phurti-feature  /phurti-fix  /phurti-audit  /phurti-memory,
               6 review agents,
               3 hooks, and the rules in ~/.claude/CLAUDE.md.
Codex CLI    - rules installed at ~/.codex/AGENTS.md (Codex also reads a project AGENTS.md).
               Skills/commands work where Codex supports the Agent Skills spec.

Two more agents (instruction-only - rules are advisory there, hooks don't apply):
  Copilot (VS Code) : copy  .github/copilot-instructions.md  into your repo
                      (or merge it into ~/.copilot/copilot-instructions.md for all repos).
  Antigravity       : 'agy plugin install <repo>', or copy  .agents/rules/phurti.md
                      into your project's .agents/rules/  (or ~/.agents/rules/).

Verify (Claude Code): open any repo and run  /phurti-feature   and   /hooks
NOTE
