"""
macOS input layer for Aerox Lite (pynput / Quartz event taps).
  * InputListener — global listener for F13–F20 (the keys the mouse sends for buttons bound to a
    macro), pointer movement (smart lighting, sensor log) and mouse buttons. Injected events
    (macros, multi-click) are ignored. macOS cannot tell which device an event came from, so the
    listener sees every mouse and trackpad.
  * parse/run — macro language and playback through pynput's keyboard/mouse controllers.
  * send_click — injected clicks for the multi-click module.
Needs Input Monitoring and Accessibility permissions. pynput is imported lazily, so parsing and the
tests work without it.
"""
import threading, time
from collections import deque

from osplatform import PERMISSION_HINT

# Synthetic codes for the macro trigger keys F13–F20 (macOS has no F21–F24).
VK_F13 = 0x10000
MAX_MACROS = 8
BTN_LEFT, BTN_RIGHT, BTN_MIDDLE = "left", "right", "middle"

# ---------------------------------------------------------------- Key table (macOS virtual key codes)
VK = {
    "a": 0x00, "s": 0x01, "d": 0x02, "f": 0x03, "h": 0x04, "g": 0x05, "z": 0x06, "x": 0x07, "c": 0x08,
    "v": 0x09, "b": 0x0B, "q": 0x0C, "w": 0x0D, "e": 0x0E, "r": 0x0F, "y": 0x10, "t": 0x11,
    "1": 0x12, "2": 0x13, "3": 0x14, "4": 0x15, "6": 0x16, "5": 0x17, "9": 0x19, "7": 0x1A, "8": 0x1C, "0": 0x1D,
    "o": 0x1F, "u": 0x20, "i": 0x22, "p": 0x23, "l": 0x25, "j": 0x26, "k": 0x28, "n": 0x2D, "m": 0x2E,
    "equals": 0x18, "minus": 0x1B, "rbracket": 0x1E, "lbracket": 0x21, "quote": 0x27, "semicolon": 0x29,
    "backslash": 0x2A, "comma": 0x2B, "slash": 0x2C, "period": 0x2F, "tilde": 0x32,
    "enter": 0x24, "tab": 0x30, "space": 0x31, "backspace": 0x33, "esc": 0x35, "escape": 0x35,
    "win": 0x37, "cmd": 0x37, "shift": 0x38, "caps": 0x39, "alt": 0x3A, "option": 0x3A, "ctrl": 0x3B,
    "insert": 0x72, "home": 0x73, "pgup": 0x74, "delete": 0x75, "del": 0x75, "end": 0x77, "pgdn": 0x79,
    "left": 0x7B, "right": 0x7C, "down": 0x7D, "up": 0x7E,
    "f1": 0x7A, "f2": 0x78, "f3": 0x63, "f4": 0x76, "f5": 0x60, "f6": 0x61, "f7": 0x62, "f8": 0x64,
    "f9": 0x65, "f10": 0x6D, "f11": 0x67, "f12": 0x6F, "f13": 0x69, "f14": 0x6B, "f15": 0x71,
    "f16": 0x6A, "f17": 0x40, "f18": 0x4F, "f19": 0x50, "f20": 0x5A,
    # Media keys are not key codes on macOS; synthetic values mapped to pynput media keys.
    "volup": 0x1001, "voldown": 0x1002, "mute": 0x1003, "play": 0x1004, "next": 0x1005, "prev": 0x1006,
}
MEDIA = {0x1001: "media_volume_up", 0x1002: "media_volume_down", 0x1003: "media_volume_mute",
         0x1004: "media_play_pause", 0x1005: "media_next", 0x1006: "media_previous"}
VK_NAMES = {}
for _k, _v in VK.items(): VK_NAMES.setdefault(_v, _k)
for _i in range(MAX_MACROS): VK_NAMES[VK_F13 + _i] = f"f{13 + _i}"
FKEY_NAMES = tuple(f"f{13 + i}" for i in range(MAX_MACROS))  # pynput Key attribute names
CLICK = {"left": BTN_LEFT, "right": BTN_RIGHT, "middle": BTN_MIDDLE}
STEP_DELAY = 0.015


def _pynput():
    try:
        from pynput import keyboard, mouse
        return keyboard, mouse
    except Exception as e:
        raise OSError(f"pynput is unavailable: {e}") from e


# ---------------------------------------------------------------- Listener
class InputListener(threading.Thread):
    """Global listener. on_move() — pointer movement; on_key(code, down) — F13–F20 as
    VK_F13 + slot; on_button(name, down) — 'left' | 'right' | 'middle'.
    If stats_on: accumulates movement in counters and queues rare events (buttons/wheel/keys) in events.
    """
    BTN = {"left": "Left click", "right": "Right click", "middle": "Middle click"}

    def __init__(self, on_move=None, on_key=None, vid=None, on_error=None, on_button=None):
        super().__init__(daemon=True)
        self.on_move, self.on_key, self.on_button, self.on_error = on_move, on_key, on_button, on_error
        self.stop_event = threading.Event()
        self.stats_lock = threading.Lock()
        self.stats_on = False
        self.n = self.dx = self.dy = self.wheel = 0
        self.pos = [0, 0]
        self.t_first = self.t_last = 0.0
        self.events = deque(maxlen=300)
        self._down, self._last = {}, None
        self._fkeys = {}
        self._listeners = []
        self.found = True

    def take_motion(self):
        """Drain accumulated movement (called once per second)."""
        with self.stats_lock:
            n, dx, dy, w, t0, t1 = self.n, self.dx, self.dy, self.wheel, self.t_first, self.t_last
            self.n = self.dx = self.dy = self.wheel = 0
            return n, dx, dy, w, (t1 - t0), tuple(self.pos)

    def stop(self):
        self.stop_event.set()

    def run(self):
        try:
            keyboard, mouse = _pynput()
            self._fkeys = {getattr(keyboard.Key, name).value.vk: i for i, name in enumerate(FKEY_NAMES)}
            if self.on_key:  # the keyboard tap needs Input Monitoring; multi-click only listens to the mouse
                self._listeners.append(keyboard.Listener(on_press=self._on_press, on_release=self._on_release))
            self._listeners.append(mouse.Listener(on_move=self._on_move_ev, on_click=self._on_click,
                                                  on_scroll=self._on_scroll))
            for lst in self._listeners: lst.start()
            for lst in self._listeners: lst.wait()
            if not all(getattr(lst, "IS_TRUSTED", True) for lst in self._listeners):
                if self.on_error: self.on_error(OSError(PERMISSION_HINT))
            self.stop_event.wait()
        except Exception as e:
            if self.on_error: self.on_error(e)
        finally:
            for lst in self._listeners:
                try: lst.stop()
                except Exception: pass

    # ---- keyboard
    def _slot(self, key):
        vk = getattr(key, "vk", None)
        if vk is None: vk = getattr(getattr(key, "value", None), "vk", None)
        return self._fkeys.get(vk)

    def _on_press(self, key, injected=False):
        slot = self._slot(key)
        if slot is None or injected: return
        if self.on_key: self.on_key(VK_F13 + slot, True)
        if self.stats_on: self.events.append(("key", VK_F13 + slot, None))

    def _on_release(self, key, injected=False):
        slot = self._slot(key)
        if slot is None or injected: return
        if self.on_key: self.on_key(VK_F13 + slot, False)

    # ---- mouse
    def _on_move_ev(self, x, y, injected=False):
        if injected: return
        last, self._last = self._last, (int(x), int(y))
        if last is None: return
        dx, dy = self._last[0] - last[0], self._last[1] - last[1]
        if not (dx or dy): return
        if self.on_move: self.on_move()
        if self.stats_on:
            t = time.perf_counter()
            with self.stats_lock:
                if not self.n: self.t_first = t
                self.t_last = t; self.n += 1
                self.dx += dx; self.dy += dy; self.pos[0] += dx; self.pos[1] += dy

    def _on_click(self, x, y, button, pressed, injected=False):
        if injected: return
        name = getattr(button, "name", str(button))
        if name not in self.BTN: return
        if self.on_button: self.on_button(name, pressed)
        if self.stats_on:
            label = self.BTN[name]
            if pressed: self._down[label] = time.perf_counter()
            else:
                t0 = self._down.pop(label, None)
                self.events.append(("btn", label, None if t0 is None else int((time.perf_counter() - t0) * 1000)))

    def _on_scroll(self, x, y, dx, dy, injected=False):
        if self.stats_on and not injected and dy:
            with self.stats_lock: self.wheel += int(dy)


# ---------------------------------------------------------------- Controllers
_ctl_lock = threading.Lock()
_ctl = {}


def _controller(kind):
    with _ctl_lock:
        if kind not in _ctl:
            keyboard, mouse = _pynput()
            _ctl[kind] = keyboard.Controller() if kind == "kbd" else mouse.Controller()
        return _ctl[kind]


def _resolve(vk):
    """macOS key code -> pynput key. Named keys (modifiers, arrows, F-keys) use the Key enum so
    pynput keeps modifier flags in sync; media keys map to their system-defined events."""
    keyboard, _ = _pynput()
    if vk in MEDIA: return getattr(keyboard.Key, MEDIA[vk])
    for k in keyboard.Key:
        if getattr(k.value, "vk", None) == vk: return k
    return keyboard.KeyCode.from_vk(vk)


def prepare_mouse():
    _controller("mouse")


def send_click(button, down):
    """Injected mouse button event (button: 'left' | 'right' | 'middle')."""
    _, mouse = _pynput()
    btn = getattr(mouse.Button, CLICK[button])
    try:
        c = _controller("mouse")
        c.press(btn) if down else c.release(btn)
    except Exception as e:
        raise OSError(f"click injection failed: {e}") from e


def close():
    with _ctl_lock: _ctl.clear()


# ---------------------------------------------------------------- Macros
def _vk(name, n):
    k = name.strip().lower()
    if k not in VK: raise ValueError("Line {0}: unknown key “{1}”".format(n, name))
    return VK[k]


def parse(text):
    ops = []
    for n, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = line.split(None, 1)
        cmd, arg = parts[0], parts[1] if len(parts) > 1 else ""
        c, arg = cmd.lower(), arg.strip()
        if c == "wait":
            try: ops.append(("wait", max(0, int(arg))))
            except ValueError: raise ValueError("Line {0}: wait requires a number (ms)".format(n))
        elif c == "text":
            ops.append(("text", arg))
        elif c in ("down", "up") and arg:
            ops.append((c, _vk(arg, n)))
        elif c == "click":
            if arg.lower() not in CLICK: raise ValueError("Line {0}: click left / right / middle".format(n))
            ops.append(("click", arg.lower()))
        else:
            ops.append(("combo", [_vk(k, n) for k in line.replace(" ", "").split("+")]))
    return ops


def key(vk, up=False):
    try:
        c = _controller("kbd")
        k = _resolve(vk)
        c.release(k) if up else c.press(k)
    except OSError:
        raise
    except Exception as e:
        raise OSError(f"key injection failed: {e}") from e


def type_text(s, stop=None):
    """Types any Unicode text (pynput sends the characters directly)."""
    c = _controller("kbd")
    for ch in s:
        if stop is not None and stop.is_set(): return
        try: c.type(ch)
        except Exception as e: raise OSError(f"text injection failed: {e}") from e
        time.sleep(0.002)


def click(btn):
    send_click(btn, True)
    time.sleep(0.01)
    send_click(btn, False)


def run(ops, stop=None):
    held = []
    try:
        for op, arg in ops:
            if stop is not None and stop.is_set(): break
            if op == "wait":
                end = time.monotonic() + arg / 1000
                while time.monotonic() < end:
                    if stop is not None and stop.is_set(): return
                    time.sleep(min(0.01, max(0, end - time.monotonic())))
                continue
            if op == "combo":
                for vk in arg:
                    key(vk); held.append(vk); time.sleep(0.005)
                for vk in reversed(arg):
                    key(vk, True); held.remove(vk)
            elif op == "down": key(arg); held.append(arg)
            elif op == "up":
                key(arg, True)
                if arg in held: held.remove(arg)
            elif op == "text": type_text(arg, stop)
            elif op == "click": click(arg)
            time.sleep(STEP_DELAY)
    finally:
        for vk in reversed(held):
            try: key(vk, True)
            except OSError: pass  # never leave keys held down


class MacroRunner:
    """Modes: once — run once; hold — repeat while the button is held; toggle — repeat on/off."""

    def __init__(self, get_macro):
        self.get, self.held, self.stops = get_macro, set(), {}
        self.lock = threading.RLock()
        self.threads = {}
        self.on_error = None

    def on_key(self, vk, down):
        with self.lock: self._on_key_locked(vk, down)

    def _on_key_locked(self, vk, down):
        if not VK_F13 <= vk <= VK_F13 + MAX_MACROS - 1: return
        slot = vk - VK_F13
        m = self.get(slot)
        if not m:
            if not down: self.held.discard(slot)
            return
        running = slot in self.stops and not self.stops[slot].is_set()
        if down:
            if slot in self.held: return  # key auto-repeat
            self.held.add(slot)
            if m["mode"] == "toggle" and running: self.stops[slot].set()
            elif not running: self._start(slot, m, loop=m["mode"] in ("hold", "toggle"))
        else:
            self.held.discard(slot)
            if m["mode"] == "hold" and running: self.stops[slot].set()

    def stop_all(self):
        with self.lock:
            for ev in self.stops.values(): ev.set()
            threads = list(self.threads.values())
        for thread in threads:
            if thread is not threading.current_thread(): thread.join(timeout=0.5)

    def _start(self, slot, m, loop):
        try: ops = parse(m["script"])
        except ValueError: return
        ev = threading.Event(); self.stops[slot] = ev

        def go():
            try:
                while not ev.is_set():
                    run(ops, ev)
                    if not loop: break
                    ev.wait(0.01)
            except Exception as e:
                if self.on_error: self.on_error(e)
            finally:
                ev.set()
        thread = threading.Thread(target=go, daemon=True)
        self.threads[slot] = thread
        thread.start()
