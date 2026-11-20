import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
START = "<!-- >>> phurti rules >>> -->"
END = "<!-- <<< phurti rules <<< -->"


def rule_block(text):
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("Expected exactly one complete Phurti rule block")
    start, end = text.index(START), text.index(END)
    if end < start:
        raise ValueError("Phurti rule markers are out of order")
    return text[start:end + len(END)]


def agent_toml(path):
    _, frontmatter, body = path.read_text(encoding="utf-8").split("---", 2)
    fields = dict(line.split(":", 1) for line in frontmatter.strip().splitlines())
    values = {
        "name": fields["name"].strip(),
        "description": fields["description"].strip(),
        "developer_instructions": body.strip(),
    }
    return "".join(f"{key} = {json.dumps(value, ensure_ascii=False)}\n" for key, value in values.items())


def agent_antigravity(path):
    _, frontmatter, body = path.read_text(encoding="utf-8").split("---", 2)
    fields = dict(line.split(":", 1) for line in frontmatter.strip().splitlines())
    values = {
        "name": fields["name"].strip(),
        "description": fields["description"].strip(),
    }
    return (
        f"---\n"
        f"name: {values['name']}\n"
        f"description: {values['description']}\n"
        f"subagent: true\n"
        f"mainAgent: false\n"
        f"tools: [read_file, run_command, manage_task]\n"
        f"---\n"
        f"{body.strip()}\n"
    )


def rendered_adapters(root=ROOT):
    rules = "# Phurti rules — apply to all code in this project\n\n"
    rules += rule_block((root / "AGENTS.md").read_text(encoding="utf-8")) + "\n"
    antigravity_rules = "---\ntrigger: always_on\n---\n" + rules
    files = {
        root / ".github/copilot-instructions.md": rules,
        root / ".agents/rules/phurti.md": antigravity_rules,
    }
    for source in sorted((root / "agents").glob("phurti-*.md")):
        files[root / "adapters/codex/agents" / (source.stem + ".toml")] = agent_toml(source)
        files[root / "adapters/antigravity/agents" / source.name] = agent_antigravity(source)
    return files


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    drift = []
    for path, content in rendered_adapters().items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                drift.append(str(path.relative_to(ROOT)))
        else:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if drift:
        parser.exit(1, "Adapter drift: " + ", ".join(drift) + "\nRun bash scripts/build-adapters.sh\n")
    print("Adapters in sync." if args.check else "Rebuilt rules, Codex review agents, and Antigravity review agents.")


if __name__ == "__main__":
    main()
