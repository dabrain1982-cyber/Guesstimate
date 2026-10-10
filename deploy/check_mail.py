"""Verify the configured GMX SMTP login without sending a message."""

from __future__ import annotations

import argparse
import smtplib
import ssl
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--secret-file", required=True)
    args = parser.parse_args()

    password = Path(args.secret_file).read_text(encoding="utf-8").strip()
    if not password:
        raise SystemExit("Die GMX-Passwortdatei ist leer.")

    context = ssl.create_default_context()
    with smtplib.SMTP("mail.gmx.net", 587, timeout=20) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(args.user, password)
    print("GMX-Anmeldung erfolgreich geprüft; es wurde keine Testmail versendet.")


if __name__ == "__main__":
    main()
