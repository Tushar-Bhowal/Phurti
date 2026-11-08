import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import sys
import tempfile

from build_adapters import END, ROOT, START, rendered_adapters, rule_block


def merge_rules(existing, block):
    if START in existing or END in existing:
        old = rule_block(existing)
        return existing.replace(old, block, 1)
    separator = "\n\n" if existing.strip() else ""
    return existing + separator + block + "\n"


def read_json(path):
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return data


def merge_hooks(settings, hook_dir, codex):
    events = settings.setdefault("hooks", {})
    if not isinstance(events, dict):
        raise ValueError("hooks must be an object")
    specifications = [
        ("PreToolUse", "Bash", "block-ai-attribution.py"),
        ("PreToolUse", "apply_patch" if codex else "Edit|MultiEdit|Write", "protect-tests.py"),
        ("SessionStart", None, "session-status.py"),
        ("PreCompact", None, "pre-compact.py"),
    ]
    names = {name for _, _, name in specifications}
    for event, groups in events.items():
        if not isinstance(groups, list):
            raise ValueError(f"hooks.{event} must be an array")
        kept = []
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                raise ValueError(f"Invalid hook group in {event}")
            handlers = []
            for handler in group["hooks"]:
                if not isinstance(handler, dict):
                    raise ValueError(f"Invalid hook handler in {event}")
                command = handler.get("command", "")
                try:
                    words = shlex.split(command) if isinstance(command, str) else []
                except ValueError:
                    words = []
                owned = any(
                    str(hook_dir / name) in words
                    or (not codex and f"~/.claude/hooks/{name}" in words)
                    for name in names
                )
                if not owned:
                    handlers.append(handler)
            if handlers:
                kept.append({**group, "hooks": handlers})
        events[event] = kept
    for event, matcher, name in specifications:
        command = "python3 " + shlex.quote(str(hook_dir / name))
        if codex:
            command += " --host codex"
        group = {"hooks": [{"type": "command", "command": command}]}
        if matcher:
            group["matcher"] = matcher
        events.setdefault(event, []).append(group)


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    if path.exists():
        shutil.copy2(path, path.with_name(path.name + ".phurti-backup"))
    fd, temporary = tempfile.mkstemp(prefix=".phurti-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def install(home, codex_home, agent):
    for path, content in rendered_adapters().items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ValueError("Adapters are stale; run bash scripts/build-adapters.sh first")
    block = rule_block((ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    pending = {}
    targets = []
    if agent in ("claude", "all"):
        targets.append((home / ".claude", home / ".claude/skills", False))
    if agent in ("codex", "all"):
        targets.append((codex_home, home / ".agents/skills", True))
    for destination, skills_dir, codex in targets:
        rules_path = destination / ("AGENTS.md" if codex else "CLAUDE.md")
        existing = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
        pending[rules_path] = merge_rules(existing, block)
        settings_path = destination / ("hooks.json" if codex else "settings.json")
        settings = read_json(settings_path)
        merge_hooks(settings, destination / "hooks", codex)
        if not codex:
            ask = settings.setdefault("permissions", {}).setdefault("ask", [])
            if not isinstance(ask, list):
                raise ValueError("permissions.ask must be an array")
            for rule in ["Read(./.env)", "Read(./.env.*)", "Bash(cat .env*)", "Bash(printenv*)", "Bash(env)"]:
                if rule not in ask:
                    ask.append(rule)
        pending[settings_path] = json.dumps(settings, indent=2, ensure_ascii=False) + "\n"
        for source in sorted((ROOT / "skills").glob("phurti-*/**/*")):
            if source.is_file():
                pending[skills_dir / source.relative_to(ROOT / "skills")] = source.read_text(encoding="utf-8")
        for source in sorted((ROOT / "hooks").glob("*.py")):
            pending[destination / "hooks" / source.name] = source.read_text(encoding="utf-8")
        agent_source = ROOT / ("adapters/codex/agents" if codex else "agents")
        for source in sorted(agent_source.glob("phurti-*")):
            pending[destination / "agents" / source.name] = source.read_text(encoding="utf-8")
    # Validate both installations before writing either host's configuration.
    for path, content in pending.items():
        write_file(path, content)
    for destination, skills_dir, codex in targets:
        print(f"{'Codex' if codex else 'Claude Code'}: five skills in {skills_dir}; six reviewers and four hooks in {destination}")
    if agent in ("codex", "all"):
        print("Codex: reload, inspect /skills, then review and trust the four hooks using /hooks.")
        print("Existing inline TOML hooks also run. Remove any manually duplicated Phurti entries there.")
        print("Codex permissions remain controlled by your sandbox and approval settings; Claude .env ask rules are not copied.")
    if agent in ("claude", "all"):
        print("Claude Code: reload, then check /phurti-feature, /agents, and /hooks.")
    print("Changed files have a sibling .phurti-backup. Personal content outside the Phurti rule block is preserved.")


def main():
    parser = argparse.ArgumentParser(description="Install Phurti skills, review agents, rules, and hooks.")
    parser.add_argument("--agent", choices=("all", "claude", "codex"), default="all")
    parser.add_argument("--home", type=Path, help="Use an alternate installation home (for staging or testing)")
    args = parser.parse_args()
    home = (args.home or Path.home()).expanduser().resolve()
    codex_home = home / ".codex"
    if args.home is None and os.environ.get("CODEX_HOME"):
        codex_home = Path(os.environ["CODEX_HOME"]).expanduser().resolve()
    try:
        install(home, codex_home, args.agent)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
