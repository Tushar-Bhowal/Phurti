#!/usr/bin/env python3
"""PreCompact hook: don't let the thread die when context is summarized away.

Fires before a manual /compact AND before automatic compaction (when the
context window fills) — the second case is the dangerous one, because it
happens without you choosing it. A hook is a script, not the model, so it
cannot write the narrative handoff itself. What it does:

  1. Tells the model to refresh .claude/handoff.md before its context goes.
  2. If no handoff exists at all, drops git breadcrumbs there so the next
     session still knows where it is. It NEVER overwrites an existing
     handoff — that would clobber the model's narrative with a stub.

Always exits 0: compaction must never be blocked.
"""
import json
import os
import subprocess
import sys

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

cwd = data.get("cwd") or os.getcwd()
trigger = data.get("trigger") or "unknown"


def git(args):
    try:
        out = subprocess.run(
            ["git", "-C", cwd] + args,
            capture_output=True, text=True, timeout=3,
        )
        return out.stdout.strip() if out.returncode == 0 else ""
    except Exception:
        return ""


handoff = os.path.join(cwd, ".claude", "handoff.md")

if not os.path.isfile(handoff) and git(["rev-parse", "--is-inside-work-tree"]) == "true":
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"]) or "(detached)"
    recent = git(["log", "-5", "--pretty=%h %s"])
    dirty = git(["status", "--porcelain"])
    try:
        os.makedirs(os.path.dirname(handoff), exist_ok=True)
        with open(handoff, "w", encoding="utf-8") as f:
            f.write("# Handoff (auto-captured at compaction)\n\n")
            f.write("No narrative handoff existed when the context was compacted, so this is\n")
            f.write("git state only. Replace it with: goal / done / next / decisions / issues.\n\n")
            f.write(f"- Branch: {branch}\n")
            if recent:
                f.write("- Recent commits:\n")
                for line in recent.splitlines():
                    f.write(f"    {line}\n")
            if dirty:
                f.write(f"- Uncommitted: {len(dirty.splitlines())} file(s)\n")
    except Exception:
        pass

print(
    f"Context is about to be compacted ({trigger} trigger). Before it is summarized "
    "away, overwrite .claude/handoff.md so the next session can resume without being "
    "re-briefed: current goal, what is done, the next 3-5 concrete tasks, key decisions "
    "and why, known issues, and how to run/test. Keep it under ~40 lines and overwrite "
    "it — never append, or it grows and costs tokens every session."
)
sys.exit(0)
