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


def merge_antigravity_hooks(settings, hook_dir):
    if not isinstance(settings, dict):
        raise ValueError("hooks must be an object")
    specifications = [
        ("phurti-attribution", "PreToolUse", "run_command", "block-ai-attribution.py"),
        ("phurti-protect-tests", "PreToolUse", "edit_file|write_file", "protect-tests.py"),
        ("phurti-status", "SessionStart", None, "session-status.py"),
    ]
    names = {name for _, _, _, name in specifications}
    to_delete = []
    for name, config in list(settings.items()):
        if name.startswith("phurti-"):
            to_delete.append(name)
            continue
        if isinstance(config, dict):
            found = False
            for handlers in config.values():
                if isinstance(handlers, list):
                    for item in handlers:
                        h_list = item.get("hooks", []) if isinstance(item, dict) and "hooks" in item else [item] if isinstance(item, dict) else []
                        for h in h_list:
                            cmd = h.get("command", "") if isinstance(h, dict) else ""
                            try:
                                words = shlex.split(cmd) if isinstance(cmd, str) else []
                            except ValueError:
                                words = []
                            if any(str(hook_dir / s) in words or s in words for s in names):
                                found = True
                                break
            if found:
                to_delete.append(name)
    for name in to_delete:
        settings.pop(name, None)
    for hook_name, event, matcher, script in specifications:
        command = "python3 " + shlex.quote(str(hook_dir / script)) + " --host antigravity"
        handler = {"type": "command", "command": command}
        if matcher:
            settings[hook_name] = {event: [{"matcher": matcher, "hooks": [handler]}]}
        else:
            settings[hook_name] = {event: [handler]}


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


def install(home, codex_home, agent="all", antigravity_home=None):
    if antigravity_home is None:
        antigravity_home = home / ".gemini/config"
    for path, content in rendered_adapters().items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            raise ValueError("Adapters are stale; run bash scripts/build-adapters.sh first")
    block = rule_block((ROOT / "AGENTS.md").read_text(encoding="utf-8"))
    pending = {}
    targets = []
    if agent in ("claude", "all"):
        targets.append((home / ".claude", home / ".claude/skills", "claude"))
    if agent in ("codex", "all"):
        targets.append((codex_home, home / ".agents/skills", "codex"))
    if agent in ("antigravity", "all"):
        targets.append((antigravity_home, antigravity_home / "skills", "antigravity"))
    for destination, skills_dir, host in targets:
        rules_path = destination / ("CLAUDE.md" if host == "claude" else "AGENTS.md")
        existing = rules_path.read_text(encoding="utf-8") if rules_path.exists() else ""
        pending[rules_path] = merge_rules(existing, block)
        settings_path = destination / ("settings.json" if host == "claude" else "hooks.json")
        settings = read_json(settings_path)
        if host == "antigravity":
            merge_antigravity_hooks(settings, destination / "hooks")
        else:
            merge_hooks(settings, destination / "hooks", codex=(host == "codex"))
            if host == "claude":
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
        if host == "codex":
            agent_source = ROOT / "adapters/codex/agents"
        elif host == "antigravity":
            agent_source = ROOT / "adapters/antigravity/agents"
        else:
            agent_source = ROOT / "agents"
        for source in sorted(agent_source.glob("phurti-*")):
            pending[destination / "agents" / source.name] = source.read_text(encoding="utf-8")
    # Validate installations before writing configuration.
    for path, content in pending.items():
        write_file(path, content)
    for destination, skills_dir, host in targets:
        display_name = "Antigravity" if host == "antigravity" else ("Codex" if host == "codex" else "Claude Code")
        hooks_count = 3 if host == "antigravity" else 4
        print(f"{display_name}: five skills in {skills_dir}; six reviewers and {hooks_count} hooks in {destination}")
    if agent in ("codex", "all"):
        print("Codex: reload, inspect /skills, then review and trust the four hooks using /hooks.")
        print("Existing inline TOML hooks also run. Remove any manually duplicated Phurti entries there.")
        print("Codex permissions remain controlled by your sandbox and approval settings; Claude .env ask rules are not copied.")
    if agent in ("claude", "all"):
        print("Claude Code: reload, then check /phurti-feature, /agents, and /hooks.")
    if agent in ("antigravity", "all"):
        print("Antigravity: reload, then check /phurti-feature, subagents in /agents, and hooks in hooks.json.")
    print("Changed files have a sibling .phurti-backup. Personal content outside the Phurti rule block is preserved.")


def main():
    parser = argparse.ArgumentParser(description="Install Phurti skills, review agents, rules, and hooks.")
    parser.add_argument("--agent", choices=("all", "claude", "codex", "antigravity"), default="all")
    parser.add_argument("--home", type=Path, help="Use an alternate installation home (for staging or testing)")
    args = parser.parse_args()
    home = (args.home or Path.home()).expanduser().resolve()
    codex_home = home / ".codex"
    if args.home is None and os.environ.get("CODEX_HOME"):
        codex_home = Path(os.environ["CODEX_HOME"]).expanduser().resolve()
    antigravity_home = home / ".gemini/config"
    if args.home is None and os.environ.get("GEMINI_CONFIG_DIR"):
        antigravity_home = Path(os.environ["GEMINI_CONFIG_DIR"]).expanduser().resolve()
    try:
        install(home, codex_home, args.agent, antigravity_home)
    except (OSError, ValueError, TypeError, AttributeError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
