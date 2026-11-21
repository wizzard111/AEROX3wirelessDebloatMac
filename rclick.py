"""
rclick.py — left/right multi-click for Aerox Lite.
A short button press -> N clicks (×2…×6, each button has its own N and toggle), like drag-clicking.
The tap threshold (tap_ms) is adjustable: shorter press = multi-click, longer = hold.
Holding works as usual (mining, bow, shield, eating in Minecraft).

The physical press always goes through untouched (the first click has no delay). osinput watches
the mouse's buttons; if a button is released faster than tap_ms, N-1 more clicks are injected from a
separate thread. Injected clicks (ours and macros) are not seen by the watcher.
The watcher runs only while the feature is on — off means zero impact on input.
"""
import os, json, time, queue, threading

from osplatform import APP_DIR

APPDIR = APP_DIR
CFG_PATH = os.path.join(APPDIR, "rclick.json")
DEFAULTS = {
    "enabled": False,
    "left_on": False,    # left button: multi-click enabled
    "right_on": True,    # right button: multi-click enabled
    "left": 3,           # left button: clicks per short press (COUNT_MIN..COUNT_MAX)
    "right": 3,          # right button: same
    "hold_ms": 8,        # how long to hold each injected click
    "gap_ms": 14,        # pause between clicks
    "tap_ms": 150,       # shorter press = tap (multi-click), longer = hold
}
COUNT_MIN, COUNT_MAX = 2, 6
TAP_MIN, TAP_MAX, TAP_STEP = 60, 400, 10
BUTTONS = ("left", "right")


def load_cfg():
    cfg = dict(DEFAULTS)
    try:
        with open(CFG_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            if "count" in data and "right" not in data:  # first-version config (right button only)
                data["right"] = data["count"]
            for b in BUTTONS:  # intermediate format: 0/1 clicks = button disabled
                if f"{b}_on" not in data and isinstance(data.get(b), int) and not isinstance(data.get(b), bool):
                    data[f"{b}_on"] = data[b] > 1
                    if data[b] < COUNT_MIN: data[b] = DEFAULTS[b]
            cfg.update({k: v for k, v in data.items() if k in DEFAULTS})
    except (OSError, ValueError):
        pass
    try:
        for k, lo, hi in (("left", COUNT_MIN, COUNT_MAX), ("right", COUNT_MIN, COUNT_MAX), ("hold_ms", 1, 100),
                          ("gap_ms", 1, 200), ("tap_ms", TAP_MIN, TAP_MAX)):
            cfg[k] = max(lo, min(hi, int(cfg[k])))
    except (TypeError, ValueError):
        cfg.update({k: DEFAULTS[k] for k in ("left", "right", "hold_ms", "gap_ms", "tap_ms")})
    for k in ("enabled", "left_on", "right_on"):
        cfg[k] = cfg[k] is True
    return cfg


def is_tap(held_ms, cfg, button="right"):
    """Short press -> how many extra clicks to send (0 = hold or button disabled)."""
    n = cfg[button]
    return n - 1 if cfg[f"{button}_on"] and held_ms < cfg["tap_ms"] and n > 1 else 0


def counts_text(cfg):
    off = "off"
    return "left {0}, right {1}".format(*(f"×{cfg[b]}" if cfg[f"{b}_on"] else off for b in BUTTONS))


class RightClickMultiplier:
    def __init__(self, log=print):
        self.log = lambda text, warn=False: log(text, warn)
        self.cfg = load_cfg()
        self._jobs = queue.Queue()
        self._listener = None
        self._worker = None
        self._down_t = {"left": None, "right": None}

    def save(self):
        os.makedirs(APPDIR, exist_ok=True)
        tmp = CFG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.cfg, f, ensure_ascii=False, indent=2)
        os.replace(tmp, CFG_PATH)

    @property
    def active(self):
        return self._listener is not None and self._listener.is_alive()

    def set_count(self, button, n):
        self.cfg[button] = max(COUNT_MIN, min(COUNT_MAX, int(n)))
        self.save()

    def set_button(self, button, on):
        self.cfg[f"{button}_on"] = bool(on)
        self.save()

    def set_tap(self, ms):
        self.cfg["tap_ms"] = max(TAP_MIN, min(TAP_MAX, int(ms)))
        self.save()

    # ---------- on / off
    def enable(self):
        if not self.active:
            try:
                import osinput
                osinput.prepare_mouse()
                self._buttons = {osinput.BTN_LEFT: "left", osinput.BTN_RIGHT: "right"}
                self._listener = osinput.InputListener(on_button=self._on_button,
                                                       on_error=lambda e: self.log("Multi-click: {0}".format(e), True))
                self._listener.start()
            except Exception as e:
                self._listener = None
                self.log("Multi-click: could not start ({0})".format(e), True)
                return False
            if self._worker is None:
                self._worker = threading.Thread(target=self._click_loop, daemon=True)
                self._worker.start()
        self.cfg["enabled"] = True
        self.save()
        self.log("Multi-click: ON ({0}; {1})".format(counts_text(self.cfg), "everywhere"))
        return True

    def _unhook(self):
        if self._listener is not None:
            self._listener.stop()
            self._listener.join(timeout=1)
            self._listener = None

    def disable(self):
        """Full disable: the watcher stops, input goes straight through."""
        self._unhook()
        self.cfg["enabled"] = False
        self.save()
        self.log("Multi-click: OFF")

    def shutdown(self):
        """App exit: stop the watcher but remember the module is enabled."""
        self._unhook()

    # ---------- watcher
    def _on_button(self, code, down):
        button = self._buttons.get(code)
        if not button or not self.cfg[f"{button}_on"]: return
        if down:
            self._down_t[button] = time.perf_counter()
        elif self._down_t[button] is not None:
            n = is_tap((time.perf_counter() - self._down_t[button]) * 1000, self.cfg, button)
            self._down_t[button] = None
            if n:
                self._jobs.put((button, n))

    def _click_loop(self):
        import osinput
        while True:
            button, n = self._jobs.get()
            hold, gap = self.cfg["hold_ms"] / 1000, self.cfg["gap_ms"] / 1000
            time.sleep(gap)                       # pause after the real click
            try:
                for i in range(n):
                    osinput.send_click(button, True)
                    time.sleep(hold)
                    osinput.send_click(button, False)
                    if i < n - 1:
                        time.sleep(gap)
            except OSError as e:
                self.log("Multi-click: {0}".format(e), True)
