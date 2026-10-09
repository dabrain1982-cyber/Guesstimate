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
EXPECTED_RELEASE="2026.10.06-flat-question-types-v2"
CADDY_FILE="/etc/caddy/Caddyfile"
CADDY_BACKUP="/etc/caddy/Caddyfile.before-guesstimate-20260930"
BACKUP_DIR="/var/backups/guesstimate"

if [[ ! -f "${SOURCE}/app.py" || ! -f "${SOURCE}/requirements.txt" || ! -f "${SOURCE}/fragen/manifest.json" ]]; then
  echo "Die Quelldateien von Stormseed´s Guesstimate wurden nicht gefunden." >&2
  exit 1
fi

/usr/bin/python3 "${SOURCE}/deploy/validate_question_library.py"

/usr/bin/caddy validate --config "${SOURCE}/deploy/Caddyfile.live" --adapter caddyfile

if ! /usr/bin/id guesstimate >/dev/null 2>&1; then
  /usr/sbin/useradd --system --home-dir "${APP_DIR}" --shell /usr/sbin/nologin --user-group guesstimate
fi

if [[ ! -f "${MAIL_SECRET_FILE}" ]]; then
  if [[ ! -t 0 ]]; then
    echo "Der GMX-Zugang fehlt. Bitte das Installationsskript in einem Terminal starten." >&2
    exit 1
  fi
  read -r -s -p "GMX-Passwort oder App-Passwort für DaBrain@gmx.net: " GMX_APP_PASSWORD
  echo
  if [[ -z "${GMX_APP_PASSWORD}" ]]; then
    echo "Ohne GMX-Passwort wird die Installation abgebrochen." >&2
    exit 1
  fi
  /usr/bin/install -o root -g guesstimate -m 0640 /dev/null "${MAIL_SECRET_FILE}"
  /usr/bin/printf '%s\n' "${GMX_APP_PASSWORD}" > "${MAIL_SECRET_FILE}"
  unset GMX_APP_PASSWORD
fi
/bin/chown root:guesstimate "${MAIL_SECRET_FILE}"
/bin/chmod 0640 "${MAIL_SECRET_FILE}"
MAIL_CHECK_SCRIPT="/run/guesstimate-check-mail.py"
/usr/bin/install -o root -g root -m 0755 \
  "${SOURCE}/deploy/check_mail.py" "${MAIL_CHECK_SCRIPT}"
if ! /usr/sbin/runuser -u guesstimate -- /usr/bin/python3 \
  "${MAIL_CHECK_SCRIPT}" \
  --user "DaBrain@gmx.net" \
  --secret-file "${MAIL_SECRET_FILE}"; then
  /bin/rm -f "${MAIL_CHECK_SCRIPT}"
  exit 1
fi
/bin/rm -f "${MAIL_CHECK_SCRIPT}"

BACKUP_STAMP="$(/usr/bin/date +%Y%m%d-%H%M%S)"
/usr/bin/install -d -o root -g root -m 0700 "${BACKUP_DIR}"
SERVICE_WAS_ACTIVE=false
if /usr/bin/systemctl is-active --quiet guesstimate.service; then
  SERVICE_WAS_ACTIVE=true
  /usr/bin/systemctl stop guesstimate.service
fi
restore_service_on_error() {
  if [[ "${SERVICE_WAS_ACTIVE}" == true ]] && ! /usr/bin/systemctl is-active --quiet guesstimate.service; then
    /usr/bin/systemctl start guesstimate.service
  fi
}
trap restore_service_on_error EXIT

if [[ -d "${APP_DIR}" ]]; then
  /usr/bin/tar -C /srv -czf "${BACKUP_DIR}/live-app-before-${BACKUP_STAMP}.tar.gz" guesstimate
fi
if [[ -f "${LIVE_DB}" ]]; then
  /bin/cp -a "${LIVE_DB}" "${BACKUP_DIR}/quiz-before-${BACKUP_STAMP}.sqlite3"
fi
/usr/bin/tar -C "${SOURCE}" -czf "${BACKUP_DIR}/source-${BACKUP_STAMP}.tar.gz" .

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

/bin/rm -rf -- "${APP_DIR}/fragen"
/usr/bin/install -d -o root -g root -m 0755 \
  "${APP_DIR}/templates" "${APP_DIR}/static" "${APP_DIR}/.deps" "${APP_DIR}/fragen"
/bin/cp -a "${SOURCE}/templates/." "${APP_DIR}/templates/"
/bin/cp -a "${SOURCE}/static/." "${APP_DIR}/static/"
/bin/cp -a "${SOURCE}/fragen/." "${APP_DIR}/fragen/"
/bin/chown -R root:root "${APP_DIR}"
/usr/bin/python3 -m pip install --disable-pip-version-check --upgrade \
  --target "${APP_DIR}/.deps" -r "${APP_DIR}/requirements.txt"

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
  /usr/sbin/runuser -u guesstimate -- /usr/bin/python3 \
    "${APP_DIR}/reset_game.py" "${LIVE_DB}"
  echo "Runden, Antworten und Highscore wurden zurückgesetzt; Logins bleiben erhalten."
fi

if [[ ! -f "${SECRET_FILE}" ]]; then
  /usr/bin/openssl rand -hex 32 > "${SECRET_FILE}"
fi
/bin/chown root:guesstimate "${SECRET_FILE}"
/bin/chmod 0640 "${SECRET_FILE}"
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
echo "Sicherungen liegen unter ${BACKUP_DIR} mit Zeitstempel ${BACKUP_STAMP}."
