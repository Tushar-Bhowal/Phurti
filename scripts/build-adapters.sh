#!/usr/bin/env bash
# Regenerates the per-agent adapter files from the single source of truth (AGENTS.md).
# Edit the rule block in AGENTS.md, then run this. Run with --check in CI to fail on drift.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Extract the marked rule block (inclusive of the marker lines) from AGENTS.md.
block="$(awk '/>>> phurti rules >>>/{f=1} f{print} /<<< phurti rules <<</{f=0}' "$ROOT/AGENTS.md")"
if [ -z "$block" ]; then echo "ERROR: rule block not found in AGENTS.md" >&2; exit 1; fi

copilot="$ROOT/.github/copilot-instructions.md"
antigravity="$ROOT/.agents/rules/phurti.md"

render() { printf '# Phurti rules — apply to all code in this project\n\n%s\n' "$block"; }

if [ "${1:-}" = "--check" ]; then
  diff <(render) "$copilot" >/dev/null 2>&1 && diff <(render) "$antigravity" >/dev/null 2>&1 \
    && { echo "Adapters in sync with AGENTS.md."; exit 0; } \
    || { echo "DRIFT: adapters differ from AGENTS.md — run scripts/build-adapters.sh" >&2; exit 1; }
fi

mkdir -p "$ROOT/.github" "$ROOT/.agents/rules"
render > "$copilot"
render > "$antigravity"
echo "Rebuilt adapters from AGENTS.md:"
echo "  $copilot"
echo "  $antigravity"
