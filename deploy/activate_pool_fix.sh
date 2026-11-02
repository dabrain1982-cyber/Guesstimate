#!/usr/bin/env bash
set -euo pipefail
[[ "$EUID" -eq 0 ]] || { echo "Bitte mit sudo starten." >&2; exit 1; }
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
[[ "$ROOT" == "/srv/guesstimate" ]] || { echo "Falscher Projektordner." >&2; exit 1; }
[[ "$#" -eq 0 ]] || { echo "Keine Optionen vorgesehen." >&2; exit 2; }
/usr/bin/python3 "$ROOT/deploy/validate_question_library.py"
/usr/bin/systemctl restart guesstimate.service
for attempt in {1..20}; do
  if /usr/bin/curl --fail --silent --max-time 2 http://127.0.0.1:8765/health; then
    printf '\n'
    /usr/sbin/runuser -u guesstimate -- /usr/bin/env PYTHONPATH="$ROOT/.deps:$ROOT" \
      /usr/bin/python3 "$ROOT/deploy/report_question_pool.py" --notify --resend \
      | /usr/bin/tee "$ROOT/deploy/pool-fix-result.log"
    exit 0
  fi
  /usr/bin/sleep 1
done
echo "Dienstprüfung fehlgeschlagen." >&2
exit 1
