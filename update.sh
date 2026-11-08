#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SRC/install.sh" "$@"
printf '\nUpdate applied. Reload your agent; review any changed Codex hooks before using them.\n'
