#!/usr/bin/env bash
set -euo pipefail

RESET_GAME=false
if [[ "${1:-}" == "--reset-game" ]]; then
  RESET_GAME=true
elif [[ "${#}" -gt 0 ]]; then
  echo "Aufruf: $0 [--reset-game]" >&2
  exit 2
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "Bitte dieses Skript mit sudo starten." >&2
  exit 1
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
APP_DIR="/srv/guesstimate"
DATA_DIR="/var/lib/guesstimate"
LIVE_DB="${DATA_DIR}/quiz.sqlite3"
SECRET_FILE="/etc/guesstimate.secret"
MAIL_SECRET_FILE="/etc/guesstimate-mail.secret"
EXPECTED_RELEASE="2026.10.03-party-5"
CADDY_FILE="/etc/caddy/Caddyfile"
CADDY_BACKUP="/etc/caddy/Caddyfile.before-guesstimate-20260930"

if [[ ! -f "${SOURCE}/app.py" || ! -f "${SOURCE}/requirements.txt" ]]; then
  echo "Die Quelldateien von Stormseed´s Guesstimate wurden nicht gefunden." >&2
  exit 1
fi

/usr/bin/caddy validate --config "${SOURCE}/deploy/Caddyfile.live" --adapter caddyfile

if ! /usr/bin/id guesstimate >/dev/null 2>&1; then
  /usr/sbin/useradd --system --home-dir "${APP_DIR}" --shell /usr/sbin/nologin --user-group guesstimate
fi

/usr/bin/install -d -o root -g root -m 0755 "${APP_DIR}" "${APP_DIR}/instance"
/usr/bin/install -d -o guesstimate -g guesstimate -m 0750 "${DATA_DIR}"
/usr/bin/install -o root -g root -m 0644 \
  "${SOURCE}/app.py" \
  "${SOURCE}/questions.py" \
  "${SOURCE}/question_expansion.py" \
  "${SOURCE}/modern_questions.py" \
  "${SOURCE}/requirements.txt" \
  "${SOURCE}/deploy/merge_player.py" \
  "${SOURCE}/deploy/reset_game.py" \
  "${APP_DIR}/"

/usr/bin/install -d -o root -g root -m 0755 "${APP_DIR}/templates" "${APP_DIR}/static"
/bin/cp -a "${SOURCE}/templates/." "${APP_DIR}/templates/"
/bin/cp -a "${SOURCE}/static/." "${APP_DIR}/static/"
/bin/chown -R root:root "${APP_DIR}"

if [[ ! -x "${APP_DIR}/.venv/bin/python" ]]; then
  /usr/bin/python3 -m venv "${APP_DIR}/.venv"
fi
"${APP_DIR}/.venv/bin/pip" install --disable-pip-version-check -r "${APP_DIR}/requirements.txt"

if [[ ! -f "${LIVE_DB}" ]]; then
  /usr/bin/install -o guesstimate -g guesstimate -m 0600 /dev/null "${LIVE_DB}"
else
  if [[ "${RESET_GAME}" != true ]]; then
    echo "Vorhandene Live-Spielstände bleiben erhalten."
  fi
fi

if [[ "${RESET_GAME}" == true ]]; then
  /usr/bin/systemctl stop guesstimate.service 2>/dev/null || true
  BACKUP_STAMP="$(/usr/bin/date +%Y%m%d-%H%M%S)"
  /bin/cp -a "${LIVE_DB}" "${LIVE_DB}.before-reset-${BACKUP_STAMP}"
  /usr/sbin/runuser -u guesstimate -- "${APP_DIR}/.venv/bin/python" \
    "${APP_DIR}/reset_game.py" "${LIVE_DB}"
  echo "Runden, Antworten und Highscore wurden zurückgesetzt; Logins bleiben erhalten."
fi

if [[ ! -f "${SECRET_FILE}" ]]; then
  /usr/bin/openssl rand -hex 32 > "${SECRET_FILE}"
fi
/bin/chown root:guesstimate "${SECRET_FILE}"
/bin/chmod 0640 "${SECRET_FILE}"
if [[ -f "${MAIL_SECRET_FILE}" ]]; then
  /bin/chown root:guesstimate "${MAIL_SECRET_FILE}"
  /bin/chmod 0640 "${MAIL_SECRET_FILE}"
else
  echo "Hinweis: ${MAIL_SECRET_FILE} fehlt; die GMX-Erschöpfungsmail bleibt bis zur Einrichtung vorgemerkt."
fi

/usr/bin/install -o root -g root -m 0644 \
  "${SOURCE}/deploy/guesstimate.service" "/etc/systemd/system/guesstimate.service"
/usr/bin/systemctl daemon-reload
/usr/bin/systemctl enable guesstimate.service
/usr/bin/systemctl restart guesstimate.service

for _ in {1..20}; do
  if /usr/bin/curl --fail --silent --show-error --max-time 2 http://127.0.0.1:8765/health >/dev/null; then
    break
  fi
  /usr/bin/sleep 1
done
LOCAL_HEALTH="$(/usr/bin/curl --fail --silent --show-error --max-time 5 http://127.0.0.1:8765/health)"
if [[ "${LOCAL_HEALTH}" != *"\"release\":\"${EXPECTED_RELEASE}\""* ]]; then
  echo "Der lokale Healthcheck meldet nicht die erwartete Version ${EXPECTED_RELEASE}." >&2
  exit 1
fi

if [[ ! -f "${CADDY_BACKUP}" ]]; then
  /bin/cp -a "${CADDY_FILE}" "${CADDY_BACKUP}"
fi
/usr/bin/install -o root -g root -m 0644 "${SOURCE}/deploy/Caddyfile.live" "${CADDY_FILE}"
/usr/bin/caddy validate --config "${CADDY_FILE}" --adapter caddyfile
/usr/bin/systemctl reload caddy.service

PUBLIC_HEALTH="$(/usr/bin/curl --fail --silent --show-error --max-time 15 \
  --resolve igroup.it-sauther.de:443:127.0.0.1 \
  https://igroup.it-sauther.de/guesstimate/health)"
if [[ "${PUBLIC_HEALTH}" != *"\"release\":\"${EXPECTED_RELEASE}\""* ]]; then
  echo "Der öffentliche Healthcheck meldet nicht die erwartete Version ${EXPECTED_RELEASE}." >&2
  exit 1
fi

echo "Stormseed´s Guesstimate ist live: https://igroup.it-sauther.de/guesstimate/"
