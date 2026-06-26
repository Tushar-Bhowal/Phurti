#!/usr/bin/env bash
# Updates an existing Phurti install to this version. Same as install.sh (idempotent +
# non-destructive) plus a reminder about what needs a restart to take effect.
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SRC/install.sh"

cat << 'NOTE'

--------------------------------------------------
UPDATE APPLIED. To make the changes take effect:

1. Restart your agent (quit and reopen) so it reloads skills, agents, and rules.
2. Verify in Claude Code, in any repo:
     /phurti-feature  /phurti-fix  /phurti-audit  /phurti-memory   appear in the menu
     /hooks    lists the 3 hooks
     /agents   lists the 6 review agents

That's it - Phurti is up to date.
--------------------------------------------------
NOTE
