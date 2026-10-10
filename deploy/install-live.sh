#!/usr/bin/env bash
set -euo pipefail
[[ "$EUID" -eq 0 ]] || { echo "Bitte mit sudo starten." >&2; exit 1; }
[[ "$#" -eq 0 ]] || { echo "Keine Optionen vorgesehen." >&2; exit 2; }
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
[[ "$ROOT" == "/srv/guesstimate" ]] || { echo "Falscher Projektordner." >&2; exit 1; }
/usr/bin/python3 "$ROOT/deploy/validate_question_library.py"
PYTHONPATH="$ROOT/.deps" /usr/bin/python3 -c 'import flask, gunicorn'
/usr/bin/systemd-analyze verify "$ROOT/deploy/guesstimate.service"
/usr/bin/ln -sfn "$ROOT/deploy/guesstimate.service" "/etc/systemd/system/guesstimate.service"
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl restart guesstimate.service
for attempt in {1..20}; do
  if /usr/bin/curl --fail --silent --max-time 2 http://127.0.0.1:8765/health; then
    exit 0
  fi
  /usr/bin/sleep 1
done
echo "Gesundheitsprüfung fehlgeschlagen." >&2
exit 1
