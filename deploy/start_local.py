"""Double-click launcher: reuse this checkout's services, start only missing ones."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
import webbrowser

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "runtime/local-launcher"
CURRENT_PREVIEW = ROOT / "deploy/local-preview.json"


class StartError(RuntimeError):
    pass


@dataclass(frozen=True)
class Service:
    name: str
    port: int
    script: Path
    asset_url: str
    asset_file: Path
    health: bool = False
    extra_args: tuple[str, ...] = ()

    @property
    def url(self):
        return f"http://127.0.0.1:{self.port}"

    @property
    def command(self):
        return [sys.executable, "-u", "-X", "utf8", str(self.script),
                "--port", str(self.port), *self.extra_args]


GAME = Service("Guesstimate", 8765, ROOT / "deploy/run_local.py",
               "/static/favicon.svg", ROOT / "static/favicon.svg", health=True)
CONQUEST = Service("Aktuelle Conquest-Vorschau", 8767, ROOT / "deploy/run_current_conquest.py",
                   "/static/favicon.svg", ROOT / "static/favicon.svg", health=True)
WORKSHOPS = (
    Service("Comic-Tafel", 8770, ROOT / "offline-preview/comic-ui-v1/serve.py",
            "/components.js", ROOT / "offline-preview/comic-ui-v1/components.js"),
    Service("Button-Werkstatt", 8771, ROOT / "offline-preview/button-workshop-v1/serve.py",
            "/renderer.js", ROOT / "offline-preview/button-workshop-v1/renderer.js"),
    Service("Conquest-Tafel (Archiv)", 8773, ROOT / "offline-preview/conquest-console-v1/serve.py",
            "/profile.json", ROOT / "offline-preview/conquest-console-v1/profile.json"),
    Service("Spielewerkstatt", 8776, ROOT / "offline-preview/game-workshop-v1/serve.py",
            "/workshop.js", ROOT / "offline-preview/game-workshop-v1/workshop.js"),
)


def game_target():
    try:
        profile = json.loads(CURRENT_PREVIEW.read_text(encoding="utf-8"))["game"] if CURRENT_PREVIEW.is_file() else "main"
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise StartError("Das aktuelle lokale Startziel konnte nicht gelesen werden.") from error
    if profile == "main":
        return GAME, GAME.url + "/"
    if profile == "conquest":
        data = ROOT / "runtime/conquest-hud-20261025"
        if not all((data / name).is_file() for name in ("walkthrough.sqlite3", "preview-cases.json")):
            raise StartError("Der gespeicherte aktuelle Conquest-Stand fehlt. Es wurde keine neue Partie angelegt.")
        return CONQUEST, CONQUEST.url + "/local/current"
    raise StartError("Unbekanntes lokales Startziel. Es wurde kein Dienst gestartet.")


def occupied(service):
    with socket.socket() as probe:
        probe.settimeout(0.4)
        return probe.connect_ex(("127.0.0.1", service.port)) == 0


def fetch(url):
    # Local services must not be routed through a system/company proxy.
    with build_opener(ProxyHandler({})).open(url, timeout=2) as response:
        return response.read(2_000_000)


def healthy(service):
    try:
        if service.health and json.loads(fetch(service.url + "/health")).get("status") != "ok":
            return False
        return hashlib.sha256(fetch(service.url + service.asset_url)).digest() == hashlib.sha256(service.asset_file.read_bytes()).digest()
    except (OSError, URLError, ValueError):
        return False


def owners(services):
    """Check occupied Windows ports without exposing unrelated command lines."""
    if not services:
        return {}
    if os.name != "nt":
        raise StartError("Die Doppelklick-Starter sind fuer Windows vorgesehen.")
    query = [{"port": service.port, "script": str(service.script)} for service in services]
    command = r"""
$ErrorActionPreference = 'Stop'
$checks = ConvertFrom-Json $env:GUESSTIMATE_LAUNCH_CHECKS
$result = @{}
foreach ($check in $checks) {
    $connections = @(Get-NetTCPConnection -State Listen -ErrorAction Stop | Where-Object LocalPort -eq $check.port)
    $matches = @()
    foreach ($connection in $connections) {
        $process = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $connection.OwningProcess)
        $expected = $check.script.Replace('/', '\').ToLowerInvariant()
        if ($process.CommandLine -and $process.CommandLine.Replace('/', '\').ToLowerInvariant().Contains($expected)) {
            $matches += [int]$connection.OwningProcess
        }
    }
    $result[[string]$check.port] = @($matches | Select-Object -Unique)
}
ConvertTo-Json -InputObject $result -Compress
"""
    env = dict(os.environ, GUESSTIMATE_LAUNCH_CHECKS=json.dumps(query))
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
            env=env, capture_output=True, text=True, timeout=20,
            creationflags=subprocess.CREATE_NO_WINDOW, check=True,
        )
        return {int(port): pids for port, pids in json.loads(result.stdout).items()}
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        raise StartError("Laufende lokale Dienste konnten nicht sicher erkannt werden. Es wurde kein weiterer gestartet.") from error


def preflight(services):
    for service in services:
        if not service.script.is_file() or not service.asset_file.is_file():
            raise StartError(f"Dateien fuer {service.name} fehlen im Projektordner.")
    active = [service for service in services if occupied(service)]
    ownership = owners(active)
    for service in active:
        if not ownership.get(service.port) or not healthy(service):
            raise StartError(f"Port {service.port} ist belegt, aber {service.name} aus diesem Ordner ist dort nicht bereit. Bitte das andere Programm pruefen; es wurde nichts beendet.")
    return active


@contextmanager
def startup_lock():
    # Windows releases this byte lock even if the window is closed mid-start.
    import msvcrt
    RUNTIME.mkdir(parents=True, exist_ok=True)
    with (RUNTIME / "start.lock").open("a+b") as handle:
        if handle.tell() == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + 45
        while True:
            try:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise StartError("Ein anderer Start dauert noch an. Bitte einen Moment warten und erneut oeffnen.")
                time.sleep(0.2)
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def stop_owned(started):
    for _, process, _ in reversed(started):
        if process.poll() is None:
            process.terminate()
    for _, process, _ in reversed(started):
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def start_missing(services, active, started):
    RUNTIME.mkdir(parents=True, exist_ok=True)
    for service in services:
        if service in active:
            print(f"{service.name}: laeuft bereits, wird weiterverwendet.", flush=True)
            continue
        log = RUNTIME / f"{service.port}-{datetime.now():%Y%m%d-%H%M%S-%f}.log"
        print(f"{service.name} startet ...", flush=True)
        with log.open("wb") as output:
            process = subprocess.Popen(service.command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT)
        started.append((service, process, log))
        deadline = time.monotonic() + 30
        while process.poll() is None and not healthy(service):
            if time.monotonic() >= deadline:
                raise StartError(f"{service.name} antwortet noch nicht. Hinweise: {log}")
            time.sleep(0.2)
        if process.poll() is not None:
            detail = log.read_text(encoding="utf-8", errors="replace")[-2500:]
            raise StartError(f"{service.name} konnte nicht starten.\n{detail}\nHinweise: {log}")


def launch(services, page, *, no_browser=False, check=False):
    started = []
    try:
        if check:
            active = preflight(services)
            for service in services:
                print(f"{service.name}: {'bereit' if service in active else 'noch nicht gestartet'}")
            return 0 if len(active) == len(services) else 1
        with startup_lock():
            active = preflight(services)
            start_missing(services, active, started)
        if not no_browser and not webbrowser.open(page):
            print(f"Bitte im Browser oeffnen: {page}", flush=True)
        print(f"Bereit: {page}", flush=True)
        if started:
            print("Dieses Fenster offenlassen. Schliessen oder Strg+C beendet die hier gestarteten Dienste. Bereits laufende Dienste bleiben bestehen.", flush=True)
        while started:
            for service, process, log in started:
                if process.poll() is not None:
                    raise StartError(f"{service.name} wurde beendet. Hinweise: {log}")
            time.sleep(0.3)
        return 0
    except KeyboardInterrupt:
        print("\nDie hier gestarteten Dienste werden beendet.", flush=True)
        return 0
    except (StartError, OSError) as error:
        print(f"\n{error}", file=sys.stderr, flush=True)
        return 1
    finally:
        stop_owned(started)


def main():
    parser = argparse.ArgumentParser(description="Lokales Guesstimate oder Werkstaetten starten")
    parser.add_argument("group", choices=("game", "workshops"))
    parser.add_argument("--no-browser", action="store_true", help="Browser nicht automatisch oeffnen")
    parser.add_argument("--check", action="store_true", help="Nur pruefen, nichts starten")
    parser.add_argument("--main-game", action="store_true", help="Hauptspiel statt aktueller Arbeitsvorschau oeffnen")
    args = parser.parse_args()
    try:
        if args.group == "game":
            service, page = (GAME, GAME.url + "/") if args.main_game else game_target()
            services = (service,)
        else:
            services, page = WORKSHOPS, WORKSHOPS[-1].url + "/#editor/buttons"
    except StartError as error:
        print(str(error), file=sys.stderr, flush=True)
        return 1
    return launch(services, page, no_browser=args.no_browser, check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
