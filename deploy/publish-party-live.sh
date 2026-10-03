#!/usr/bin/env bash
set -euo pipefail

if [[ "${EUID}" -ne 0 ]]; then
  echo "Bitte dieses Skript mit sudo starten." >&2
  exit 1
fi

SOURCE="/home/igroup/Rate it"
LIVE_DB="/var/lib/guesstimate/quiz.sqlite3"
STAMP="$(/usr/bin/date +%Y%m%d-%H%M%S)"

/usr/bin/systemctl stop guesstimate.service
trap '/usr/bin/systemctl start guesstimate.service' EXIT
/usr/bin/env \
  PYTHONPATH="${SOURCE}/.deps" \
  /usr/bin/python3 "${SOURCE}/deploy/merge_player.py" --check \
  "${LIVE_DB}" "Pearlyde" "Pearlyde1"
/bin/cp -a "${LIVE_DB}" "${LIVE_DB}.before-pearlyde-merge-${STAMP}"
/usr/bin/systemctl start guesstimate.service
trap - EXIT

"${SOURCE}/deploy/install-live.sh"

/usr/bin/systemctl stop guesstimate.service
trap '/usr/bin/systemctl start guesstimate.service' EXIT
/usr/sbin/runuser -u guesstimate -- /usr/bin/env \
  PYTHONPATH="/srv/guesstimate/.deps" MERGE_NEW_PIN="1234" \
  /usr/bin/python3 "/srv/guesstimate/merge_player.py" \
  "${LIVE_DB}" "Pearlyde" "Pearlyde1"

/usr/bin/systemctl start guesstimate.service
trap - EXIT

for _ in {1..20}; do
  if /usr/bin/curl --fail --silent --max-time 2 http://127.0.0.1:8765/health >/dev/null; then
    break
  fi
  /usr/bin/sleep 1
done
/usr/bin/curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8765/health
echo
echo "Neue Version veröffentlicht und Pearlyde zusammengeführt."
