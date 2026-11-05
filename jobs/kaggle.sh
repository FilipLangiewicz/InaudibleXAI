#!/usr/bin/env bash
# Run the Kaggle CLI of the project with the correct account.
# Usage: bash jobs/kaggle.sh <arguments of the kaggle command>
# If .env of the project has KAGGLE_API_TOKEN, the CLI uses this token.
# Otherwise the CLI uses the personal credentials (~/.kaggle/access_token).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ -f "$ROOT/.env" ]; then
  TOKEN="$(sed -n 's/^KAGGLE_API_TOKEN=//p' "$ROOT/.env" | tr -d '[:space:]"'"'")"
  [ -n "$TOKEN" ] && export KAGGLE_API_TOKEN="$TOKEN"
fi
for KAGGLE in "$ROOT/.venv/Scripts/kaggle.exe" "$ROOT/.venv/bin/kaggle"; do
  [ -x "$KAGGLE" ] && exec "$KAGGLE" "$@"
done
echo "kaggle.sh: no Kaggle CLI in $ROOT/.venv" >&2
exit 127
