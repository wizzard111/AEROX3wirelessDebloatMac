"""Tests for the macOS layer: key tables, listener callbacks, LaunchAgent, notifications."""
import os
from pathlib import Path
import plistlib
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import osinput
import osplatform


class KeyTableTests(unittest.TestCase):
    def test_mac_key_codes(self):
        self.assertEqual(osinput.VK['a'], 0x00)
        self.assertEqual(osinput.VK['c'], 0x08)
        self.assertEqual(osinput.VK['enter'], 0x24)
        self.assertEqual(osinput.VK['ctrl'], 0x3B)
        self.assertEqual(osinput.VK['win'], osinput.VK['cmd'])
        self.assertEqual(osinput.VK['f13'], 0x69)
        self.assertEqual(osinput.VK['f20'], 0x5A)
        self.assertNotIn('f21', osinput.VK)
        self.assertNotIn('printscreen', osinput.VK)

    def test_macro_trigger_names(self):
        self.assertEqual(osinput.MAX_MACROS, 8)
        self.assertEqual(osinput.VK_NAMES[osinput.VK_F13], 'f13')
        self.assertEqual(osinput.VK_NAMES[osinput.VK_F13 + 7], 'f20')

    def test_parse_rejects_keys_missing_on_mac(self):
        with self.assertRaisesRegex(ValueError, 'Line 2'):
            osinput.parse('ctrl+c\nf24')


class ListenerTests(unittest.TestCase):
    def make(self):
        self.moves, self.keys, self.buttons = [], [], []
        lst = osinput.InputListener(lambda: self.moves.append(1), lambda c, d: self.keys.append((c, d)),
                                    on_button=lambda b, d, t=None: self.buttons.append((b, d)))
        return lst

    def test_macro_keys_from_key_codes(self):
        """KeyTap passes real key presses as macOS key codes (injected ones never reach here)."""
        lst = self.make(); lst.stats_on = True
        lst._on_keycode(0x6B, True)        # F14
        lst._on_keycode(0x6B, False)
        lst._on_keycode(0x00, True)        # 'a': not a macro key
        lst._on_keycode(0x5A, True)        # F20: the last macro key
        self.assertEqual(self.keys, [(osinput.VK_F13 + 1, True), (osinput.VK_F13 + 1, False), (osinput.VK_F13 + 7, True)])
        self.assertEqual([e[1] for e in lst.events], [osinput.VK_F13 + 1, osinput.VK_F13 + 7])

    def test_key_codes_of_all_macro_keys(self):
        self.assertEqual(sorted(osinput.FKEY_CODES.values()), list(range(osinput.MAX_MACROS)))
        self.assertEqual(osinput.FKEY_CODES[0x69], 0)

    def test_keyboard_controller_never_made_off_the_main_thread(self):
        """pynput reads the keyboard layout when its controller is created; macOS ends the process if
        that happens off the main thread. It must fail cleanly instead."""
        import threading
        osinput.close()
        result = []
        def worker():
            try: osinput._controller("kbd"); result.append("made")
            except OSError as e: result.append(str(e))
        t = threading.Thread(target=worker); t.start(); t.join()
        self.assertIn("not ready", result[0])

    def test_no_pynput_keyboard_listener(self):
        src = (ROOT / "src" / "osinput.py").read_text(encoding="utf-8")
        self.assertNotIn("keyboard.Listener(", src)

    def test_clicks_skip_injected(self):
        lst = self.make(); lst.stats_on = True
        right = types.SimpleNamespace(name='right')
        lst._on_click(0, 0, right, True, False)
        lst._on_click(0, 0, right, True, True)    # our own multi-click
        lst._on_click(0, 0, right, False, False)
        self.assertEqual(self.buttons, [('right', True), ('right', False)])
        self.assertEqual([e[0] for e in lst.events], ['btn'])

    def test_motion_from_positions(self):
        lst = self.make(); lst.stats_on = True
        lst._on_move_ev(100, 100)                  # first position: reference only
        lst._on_move_ev(103, 98)
        lst._on_move_ev(103, 98)                   # no change
        lst._on_move_ev(110, 90, True)             # injected
        self.assertEqual(self.moves, [1])
        n, dx, dy, w, dt, pos = lst.take_motion()
        self.assertEqual((n, dx, dy), (1, 3, -2))

    def test_macro_runner_slot_range(self):
        started = []
        r = osinput.MacroRunner(lambda slot: {'mode': 'once', 'script': 'wait 1'})
        r._start = lambda slot, m, loop: started.append(slot)
        r.on_key(osinput.VK_F13 + 7, True)
        r.on_key(osinput.VK_F13 + 8, True)  # beyond F20
        self.assertEqual(started, [7])


class PlatformTests(unittest.TestCase):
    def test_launch_agent(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, 'LaunchAgents', 'io.github.aeroxlite.plist')
            with patch.object(osplatform, 'AUTOSTART_FILE', path):
                osplatform.set_autostart(True, 'aerox_lite.py')
                with open(path, 'rb') as f: data = plistlib.load(f)
                self.assertEqual(data['Label'], 'io.github.aeroxlite')
                self.assertTrue(data['RunAtLoad'])
                self.assertEqual(data['ProgramArguments'][-1], '--tray')
                osplatform.set_autostart(False, 'x')
                self.assertFalse(os.path.exists(path))

    def test_notification_is_escaped(self):
        calls = []
        with patch.object(osplatform.subprocess, 'Popen', lambda cmd, **kw: calls.append(cmd)):
            osplatform.notify('Say "hi" \\ now', 'Aerox')
        self.assertEqual(calls[0][:2], ['osascript', '-e'])
        self.assertEqual(calls[0][2], 'display notification "Say \\"hi\\" \\\\ now" with title "Aerox"')

    @unittest.skipUnless(os.name == 'posix', 'fcntl locking is POSIX-only')
    def test_single_instance(self):
        with tempfile.TemporaryDirectory() as d, patch.object(osplatform, 'APP_DIR', d):
            a = osplatform.SingleInstance()
            b = osplatform.SingleInstance()
            self.assertTrue(a.acquired)
            self.assertFalse(b.acquired)
            a.release()


class DisplayScaleTests(unittest.TestCase):
    def test_retina_needs_no_correction(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop('AEROX_SCALE', None)
            self.assertIsNone(osplatform.display_scale(None, 1.0))
        with patch.dict(os.environ, {'AEROX_SCALE': '1.5'}):
            self.assertEqual(osplatform.display_scale(None, 1.0), 1.5)


if __name__ == '__main__':
    unittest.main()
