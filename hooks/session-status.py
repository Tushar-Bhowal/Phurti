#!/usr/bin/env python3
"""SessionStart hook: print git status and the last session's handoff.

For SessionStart, stdout is injected as context Claude can see — so after a
/clear, a compaction, or on startup/resume, Claude isn't starting blind. It
prints two things: plain git facts (branch, last commit, dirty files), and
whatever the previous session left in .claude/handoff.md. That handoff is what
makes resuming free: you never re-paste context. Kept fast and small, no
repo-wide scans, and the handoff is truncated so a bloated one can't quietly
eat the context window. Always exits 0 (never blocks a session).
"""
import os
import subprocess
import sys

MAX_HANDOFF_CHARS = 6000


def git(args):
    try:
        out = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=3,
        )
        if out.returncode != 0:
            return ""
        return out.stdout.strip()
    except Exception:
        return ""


if git(["rev-parse", "--is-inside-work-tree"]) == "true":
    branch = git(["rev-parse", "--abbrev-ref", "HEAD"]) or "(detached)"
    last = git(["log", "-1", "--pretty=%h %s"])
    porcelain = git(["status", "--porcelain"])

    changed = [ln[2:].lstrip() for ln in porcelain.splitlines() if ln.strip()]
    lines = ["Session status (from git):", f"- Branch: {branch}"]
    if last:
        lines.append(f"- Last commit: {last}")
    if changed:
        shown = ", ".join(changed[:5])
        more = f" (+{len(changed) - 5} more)" if len(changed) > 5 else ""
        lines.append(f"- Uncommitted changes: {len(changed)} file(s): {shown}{more}")
    else:
        lines.append("- Working tree clean")
    print("\n".join(lines))

handoff = os.path.join(os.getcwd(), ".claude", "handoff.md")
if os.path.isfile(handoff):
    try:
        with open(handoff, encoding="utf-8", errors="ignore") as f:
            text = f.read().strip()
    except Exception:
        text = ""
    if text:
        if len(text) > MAX_HANDOFF_CHARS:
            text = text[:MAX_HANDOFF_CHARS].rstrip() + "\n...(truncated - keep handoff.md under ~40 lines)"
        print("\nResuming from .claude/handoff.md - where the last session left off:\n")
        print(text)

sys.exit(0)
