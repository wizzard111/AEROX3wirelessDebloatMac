"""Tests for V5 modules: smart battery, rclick logic, helpers."""
import copy
import json
import os
from pathlib import Path
import queue
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.modules.setdefault('hid', types.SimpleNamespace(enumerate=lambda *_: []))
sys.modules.setdefault('hidraw', sys.modules['hid'])
sys.modules.setdefault('pystray', types.SimpleNamespace())
import helpers
import rclick
import smartbattery
import aerox_lite as app


class Tmp(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.patches = [patch.object(m, 'APPDIR', d) for m in (helpers, rclick, smartbattery)]
        self.patches += [
            patch.object(helpers, 'STATE_PATH', os.path.join(d, 'helpers.json')),
            patch.object(rclick, 'CFG_PATH', os.path.join(d, 'rclick.json')),
            patch.object(smartbattery, 'CFG_PATH', os.path.join(d, 'smartbattery.json')),
            patch.object(smartbattery, 'LOG_PATH', os.path.join(d, 'battery_log.json')),
        ]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in self.patches: p.stop()
        self.tmp.cleanup()


class BatteryTests(Tmp):
    def make(self):
        self.now = getattr(self, 'now', [1_000_000.0])
        self.events = getattr(self, 'events', [])
        self.notes = getattr(self, 'notes', [])
        return smartbattery.SmartBattery(self.events.append, lambda *a: None, self.notes.append, clock=lambda: self.now[0])

    def test_forecast_and_hysteresis(self):
        sb = self.make()
        level = 40
        for i in range(600):                      # 1 sample/min, ~3 %/h
            self.now[0] = 1_000_000 + i * 60
            level = 40 - i // 20
            sb.update(level, False)
        self.assertEqual(self.events, [True])     # saver turned on once — below 25%
        self.assertEqual(len(self.notes), 1)
        self.assertIn('24%', self.notes[0])       # "battery low" notification
        self.assertAlmostEqual(sb.hours_left(), level / 3, delta=0.5)
        sb.update(21, False); sb.update(25, False)
        self.assertEqual(self.events, [True])     # between 25 and 30 — no flapping
        sb.update(25, True)
        self.assertEqual(self.events, [True, False])
        self.assertEqual(len(self.notes), 2)      # "charging — saver off"
        self.assertEqual(sb.forecast_text(), 'charging')

    def test_low_state_survives_restart_and_disable_restores(self):
        sb = self.make(); sb.update(25, False)
        self.assertEqual(self.events, [])         # exactly 25% — not yet
        sb.update(20, False)
        sb2 = self.make()
        self.assertTrue(sb2.low_active)
        sb2.set_enabled(False)
        self.assertEqual(self.events, [True, False])
        self.assertFalse(helpers.module_on('battery'))

    def test_saver_snapshot_and_apply(self):
        a = app.App.__new__(app.App); a.cfg = copy.deepcopy(app.DEFAULT); a.jobs = queue.Queue(); a.saver = True
        a.enqueue({'poll', 'light'})
        cats, save, cfg = a.jobs.get_nowait()
        self.assertTrue(cfg['_saver'])
        sent = []
        m = types.SimpleNamespace(connected=lambda: True, generic=False, set_poll=sent.append,
                                  set_reactive=lambda *_: None, set_zone=lambda z, c, fast=False: sent.append(c),
                                  set_default_light=lambda *_: None)
        a.mouse, a.log, a.post = m, lambda *_: None, lambda *_: None
        a._apply_locked(cats, False, cfg)
        self.assertEqual(sent[0], 500)
        self.assertEqual(sent[1:], [(0, 0, 0)] * 3)
        self.assertNotIn('_saver', a.cfg)  # never written to config


class RclickTests(Tmp):
    def test_tap_vs_hold_per_button(self):
        cfg = rclick.load_cfg()
        self.assertNotIn('apps', cfg)
        self.assertFalse(cfg['enabled'])
        self.assertEqual(rclick.is_tap(40, cfg, 'right'), 2)   # right ×3: 1 real + 2 injected
        self.assertEqual(rclick.is_tap(40, cfg, 'left'), 0)    # left is off by default
        cfg['left_on'], cfg['left'] = True, 6
        self.assertEqual(rclick.is_tap(40, cfg, 'left'), 5)    # left ×6
        self.assertEqual(rclick.is_tap(400, cfg, 'left'), 0)   # holds (mining) are left alone
        cfg['tap_ms'] = 60
        self.assertEqual(rclick.is_tap(80, cfg, 'left'), 0)    # adjustable tap threshold

    def test_ranges_and_setters(self):
        rc = rclick.RightClickMultiplier(lambda *a: None)
        rc.set_count('left', 9); rc.set_tap(5); rc.set_button('left', True)
        cfg = rclick.load_cfg()
        self.assertEqual((cfg['left'], cfg['tap_ms'], cfg['left_on']), (rclick.COUNT_MAX, rclick.TAP_MIN, True))
        self.assertEqual(rclick.counts_text(cfg), 'left ×6, right ×3')

    def test_bad_and_old_configs(self):
        Path(rclick.CFG_PATH).write_text('{"count": "x", "apps": 5, "enabled": "yes"}', encoding='utf-8')
        cfg = rclick.load_cfg()
        self.assertEqual(cfg['right'], 3); self.assertNotIn('apps', cfg)
        self.assertFalse(cfg['enabled'])
        Path(rclick.CFG_PATH).write_text('{"count": 5, "enabled": true}', encoding='utf-8')   # first V5 format
        cfg = rclick.load_cfg()
        self.assertEqual((cfg['right'], cfg['right_on'], cfg['left_on']), (5, True, False))
        Path(rclick.CFG_PATH).write_text('{"left": 0, "right": 4}', encoding='utf-8')         # 0 = button off
        cfg = rclick.load_cfg()
        self.assertEqual((cfg['left_on'], cfg['left'], cfg['right_on'], cfg['right']), (False, 3, True, 4))


class V5FixTests(Tmp):
    def test_multiclick_everywhere_by_default(self):
        cfg = rclick.load_cfg()
        self.assertNotIn('only_apps', cfg)
        self.assertNotIn('apps', cfg)

    def test_tray_toggles_only_multiclick(self):
        self.assertEqual(set(helpers.TRAY_MODULES), {'rclick'})
        self.assertNotIn('directional', helpers.MODULES)

    def test_battery_estimate_before_learning(self):
        sb = smartbattery.SmartBattery(lambda a: None, lambda *a: None, clock=lambda: 1e6)
        sb.update(80, False)
        txt = sb.forecast_text()
        self.assertIn('(estimate)', txt)                 # estimate shown immediately, not "collecting data"
        self.assertAlmostEqual(sb.hours_left(), 80 / smartbattery.DEFAULT_RATE, places=3)


class HelpersTests(Tmp):
    def test_defaults_and_recall(self):
        self.assertTrue(helpers.module_on('battery'))
        self.assertFalse(helpers.module_on('rclick'))
        helpers.remember(['rclick', 'battery', 'bogus'])
        self.assertEqual(helpers.recall(), ['rclick', 'battery'])
        helpers.remember(None)
        self.assertEqual(helpers.recall(), [])


if __name__ == '__main__':
    unittest.main()
