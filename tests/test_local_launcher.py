"""Startup safety: preserve existing services and clean up only owned children."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("local_launcher", Path(__file__).resolve().parents[1] / "deploy/start_local.py")
launcher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = launcher
SPEC.loader.exec_module(launcher)


class LocalLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (launcher.ROOT / "runtime").mkdir(exist_ok=True)

    def test_existing_game_opens_browser_without_start_or_stop(self):
        with patch.object(launcher, "startup_lock") as lock, patch.object(launcher, "preflight", return_value=[launcher.GAME]), patch.object(launcher.subprocess, "Popen") as spawn, patch.object(launcher.webbrowser, "open", return_value=True) as browser, patch.object(launcher, "stop_owned", wraps=launcher.stop_owned) as stop:
            lock.return_value.__enter__.return_value = None
            self.assertEqual(launcher.launch((launcher.GAME,), launcher.GAME.url), 0)
            spawn.assert_not_called()
            browser.assert_called_once_with(launcher.GAME.url)
            stop.assert_called_once_with([])

    def test_foreign_port_aborts_entire_group_before_any_start(self):
        services = launcher.WORKSHOPS
        with patch.object(launcher, "startup_lock"), patch.object(launcher, "occupied", side_effect=lambda service: service is services[1]), patch.object(launcher, "owners", return_value={}), patch.object(launcher.subprocess, "Popen") as spawn, patch.object(launcher.webbrowser, "open") as browser:
            self.assertEqual(launcher.launch(services, "http://127.0.0.1:8771/sammlung"), 1)
            spawn.assert_not_called()
            browser.assert_not_called()

    def test_matching_process_with_wrong_response_is_not_adopted(self):
        with patch.object(launcher, "occupied", return_value=True), patch.object(launcher, "owners", return_value={8765: [42]}), patch.object(launcher, "healthy", return_value=False):
            with self.assertRaises(launcher.StartError):
                launcher.preflight((launcher.GAME,))

    def test_failed_child_is_cleaned_up_and_browser_stays_closed(self):
        process = Mock()
        process.poll.return_value = 1
        with tempfile.TemporaryDirectory(dir=launcher.ROOT / "runtime") as directory, patch.object(launcher, "RUNTIME", Path(directory)), patch.object(launcher, "startup_lock"), patch.object(launcher, "preflight", return_value=[]), patch.object(launcher.subprocess, "Popen", return_value=process), patch.object(launcher.webbrowser, "open") as browser:
            self.assertTrue(Path(directory).resolve().is_relative_to(launcher.ROOT / "runtime"))
            self.assertEqual(launcher.launch((launcher.GAME,), launcher.GAME.url), 1)
            process.wait.assert_called_once()
            process.terminate.assert_not_called()
            browser.assert_not_called()

    def test_timeout_terminates_owned_child_only(self):
        process = Mock()
        process.poll.return_value = None
        with tempfile.TemporaryDirectory(dir=launcher.ROOT / "runtime") as directory, patch.object(launcher, "RUNTIME", Path(directory)), patch.object(launcher, "startup_lock"), patch.object(launcher, "preflight", return_value=[launcher.WORKSHOPS[0]]), patch.object(launcher.subprocess, "Popen", return_value=process) as spawn, patch.object(launcher, "healthy", return_value=False), patch.object(launcher.time, "monotonic", side_effect=[0, 31]), patch.object(launcher.webbrowser, "open") as browser:
            self.assertTrue(Path(directory).resolve().is_relative_to(launcher.ROOT / "runtime"))
            self.assertEqual(launcher.launch(launcher.WORKSHOPS[:2], "unused"), 1)
            self.assertEqual(spawn.call_count, 1)
            process.terminate.assert_called_once()
            process.wait.assert_called_once()
            browser.assert_not_called()

    def test_paths_with_spaces_are_passed_as_arguments(self):
        service = launcher.Service("Test", 12345, Path("C:/Projekt mit Leerzeichen/serve.py"), "/test", Path("unused"))
        self.assertEqual(service.command[4], str(service.script))
        self.assertEqual(service.command[5:], ["--port", "12345"])

    def test_check_never_starts_or_opens_browser(self):
        with patch.object(launcher, "preflight", return_value=[]), patch.object(launcher, "startup_lock") as lock, patch.object(launcher.subprocess, "Popen") as spawn, patch.object(launcher.webbrowser, "open") as browser:
            self.assertEqual(launcher.launch((launcher.GAME,), "unused", check=True), 1)
            spawn.assert_not_called()
            lock.assert_not_called()
            browser.assert_not_called()

    def test_current_conquest_target_resumes_existing_saved_preview(self):
        with tempfile.TemporaryDirectory(dir=launcher.ROOT / "runtime") as directory:
            root = Path(directory)
            config = root / "current.json"
            config.write_text(json.dumps({"game": "conquest"}), encoding="utf-8")
            data = root / "runtime/conquest-hud-20261025"
            data.mkdir(parents=True)
            for name in ("walkthrough.sqlite3", "preview-cases.json"):
                (data / name).touch()
            with patch.object(launcher, "ROOT", root), patch.object(launcher, "CURRENT_PREVIEW", config):
                self.assertEqual(launcher.game_target(), (launcher.CONQUEST, "http://127.0.0.1:8767/local/current"))
            self.assertNotIn("--prepare", launcher.CONQUEST.command)

    def test_missing_current_save_aborts_instead_of_creating_another_game(self):
        with tempfile.TemporaryDirectory(dir=launcher.ROOT / "runtime") as directory:
            root = Path(directory)
            config = root / "current.json"
            config.write_text('{"game":"conquest"}', encoding="utf-8")
            with patch.object(launcher, "ROOT", root), patch.object(launcher, "CURRENT_PREVIEW", config):
                with self.assertRaises(launcher.StartError):
                    launcher.game_target()
            self.assertFalse((root / "runtime").exists())

    def test_unknown_target_fails_and_main_game_remains_explicitly_available(self):
        with tempfile.TemporaryDirectory(dir=launcher.ROOT / "runtime") as directory:
            config = Path(directory) / "current.json"
            config.write_text('{"game":"unknown"}', encoding="utf-8")
            with patch.object(launcher, "CURRENT_PREVIEW", config):
                with self.assertRaises(launcher.StartError):
                    launcher.game_target()
            with patch.object(sys, "argv", ["start_local.py", "game", "--main-game"]), patch.object(launcher, "launch", return_value=0) as launch, patch.object(launcher, "game_target") as target:
                self.assertEqual(launcher.main(), 0)
                target.assert_not_called()
                launch.assert_called_once_with((launcher.GAME,), launcher.GAME.url + "/", no_browser=False, check=False)

    def test_game_main_opens_selected_current_target(self):
        with patch.object(sys, "argv", ["start_local.py", "game"]), patch.object(launcher, "game_target", return_value=(launcher.CONQUEST, launcher.CONQUEST.url + "/local/current")), patch.object(launcher, "launch", return_value=0) as launch:
            self.assertEqual(launcher.main(), 0)
            launch.assert_called_once_with((launcher.CONQUEST,), launcher.CONQUEST.url + "/local/current", no_browser=False, check=False)

    def test_workshop_shortcut_opens_the_shared_workshop(self):
        with patch.object(sys,'argv',['start_local.py','workshops']),patch.object(launcher,'launch',return_value=0) as launch:
            self.assertEqual(launcher.main(),0)
            launch.assert_called_once_with(launcher.WORKSHOPS,'http://127.0.0.1:8776/#editor/buttons',no_browser=False,check=False)


if __name__ == "__main__":
    unittest.main()
