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
sys.path.insert(0, str(ROOT))
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
                                    on_button=lambda b, d: self.buttons.append((b, d)))
        lst._fkeys = {0x69: 0, 0x6B: 1}  # f13, f14 (filled from pynput in run())
        return lst

    def test_macro_keys_and_injected_events(self):
        lst = self.make(); lst.stats_on = True
        f14 = types.SimpleNamespace(vk=0x6B)
        lst._on_press(f14, False)
        lst._on_release(f14, False)
        lst._on_press(f14, True)                                  # injected: ignored
        lst._on_press(types.SimpleNamespace(vk=0x00), False)      # 'a': ignored
        self.assertEqual(self.keys, [(osinput.VK_F13 + 1, True), (osinput.VK_F13 + 1, False)])

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


if __name__ == '__main__':
    unittest.main()
