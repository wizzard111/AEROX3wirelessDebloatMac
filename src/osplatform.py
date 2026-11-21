"""macOS integration: config folder, autostart, single instance, notifications, fonts.
Standard library only, so every module can import it cheaply."""
import os
import plistlib
import subprocess
import sys

NAME = "macOS"
# Exit right after saving: the Tk/Cocoa/pystray teardown at exit can crash on macOS.
FAST_EXIT = True
APP_DIR = os.path.expanduser("~/Library/Application Support/AeroxLite")

# Tk on macOS renders point sizes smaller than on Windows, hence the size delta.
FONT = "Helvetica Neue"
MONO = "Menlo"
FONT_SIZE_DELTA = 3
TRAY_FONTS = ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
              "/System/Library/Fonts/Helvetica.ttc", "Arial Bold.ttf")

AGENT_LABEL = "io.github.aeroxlite"
AUTOSTART_FILE = os.path.expanduser(f"~/Library/LaunchAgents/{AGENT_LABEL}.plist")


def launch_command(script):
    """Command line that starts the app in the tray (app bundle binary or python + script)."""
    if getattr(sys, "frozen", False):
        return [sys.executable, "--tray"]
    return [sys.executable, os.path.abspath(script), "--tray"]


def set_autostart(on, script):
    """A per-user LaunchAgent that starts Aerox Lite at login."""
    try:
        if on:
            os.makedirs(os.path.dirname(AUTOSTART_FILE), exist_ok=True)
            with open(AUTOSTART_FILE, "wb") as f:
                plistlib.dump({"Label": AGENT_LABEL, "ProgramArguments": launch_command(script),
                               "RunAtLoad": True, "ProcessType": "Interactive"}, f)
        elif os.path.exists(AUTOSTART_FILE):
            os.remove(AUTOSTART_FILE)
    except OSError as e:
        raise OSError(str(e)) from e


class SingleInstance:
    """Exclusive lock on a file in APP_DIR; released automatically when the process exits."""

    def __init__(self):
        import fcntl
        os.makedirs(APP_DIR, exist_ok=True)
        self._f = open(os.path.join(APP_DIR, "instance.lock"), "w")
        try:
            fcntl.flock(self._f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.acquired = True
        except OSError:
            self.acquired = False
            self._f.close()

    def release(self):
        if self.acquired:
            self._f.close()
            self.acquired = False


def _applescript_string(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def notify(text, title="Aerox Lite"):
    """Notification Center message via osascript. Silently ignored on failure."""
    script = f"display notification {_applescript_string(text)} with title {_applescript_string(title)}"
    try:
        subprocess.Popen(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def gg_running():
    try:
        r = subprocess.run(["pgrep", "-if", "SteelSeries ?GG|SteelSeriesEngine"], capture_output=True, timeout=3)
        return r.returncode == 0
    except Exception:
        return False


def display_scale(root, tk_scaling):
    """macOS renders Tk in points, so Retina screens need no correction.
    AEROX_SCALE=1.5 (or another factor) still allows a manual override."""
    try:
        v = float(os.environ.get("AEROX_SCALE", ""))
        return max(0.5, min(4.0, v)) if v > 0 else None
    except ValueError:
        return None


def input_permissions(prompt=False):
    """(input_monitoring, accessibility): True/False, or None if unknown.
    prompt=True makes macOS show its own permission dialogs for this app (only the user can grant them;
    a script cannot, and permissions belong to the app that asks)."""
    import ctypes
    im = ax = None
    try:  # Input Monitoring: IOHIDCheckAccess / IOHIDRequestAccess (macOS 10.15+)
        iokit = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/IOKit.framework/IOKit")
        iokit.IOHIDCheckAccess.argtypes = iokit.IOHIDRequestAccess.argtypes = [ctypes.c_uint32]
        iokit.IOHIDCheckAccess.restype, iokit.IOHIDRequestAccess.restype = ctypes.c_uint32, ctypes.c_bool
        LISTEN_EVENT, GRANTED = 1, 0
        im = iokit.IOHIDCheckAccess(LISTEN_EVENT) == GRANTED
        if not im and prompt: im = bool(iokit.IOHIDRequestAccess(LISTEN_EVENT))
    except Exception:
        pass
    try:  # Accessibility: needed to send keys/clicks (macros, multi-click)
        from ApplicationServices import AXIsProcessTrustedWithOptions, kAXTrustedCheckOptionPrompt
        ax = bool(AXIsProcessTrustedWithOptions({kAXTrustedCheckOptionPrompt: bool(prompt)}))
    except Exception:
        try:
            hi = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices")
            hi.AXIsProcessTrusted.restype = ctypes.c_bool
            ax = bool(hi.AXIsProcessTrusted())
        except Exception:
            pass
    return im, ax


def open_privacy_settings():
    """Open the Privacy & Security panes the user has to switch on."""
    for pane in ("Privacy_ListenEvent", "Privacy_Accessibility"):
        try: subprocess.Popen(["open", f"x-apple.systempreferences:com.apple.preference.security?{pane}"])
        except OSError: pass


def tray_available():
    return True  # the menu bar is always there


def tray_text(text):
    return text


def style_window(win):
    pass


def setup_root(root, show, quit):
    """Dock icon click reopens the window; Cmd+Q / the app menu quits cleanly."""
    try:
        root.createcommand("tk::mac::ReopenApplication", show)
        root.createcommand("tk::mac::Quit", quit)
    except Exception:
        pass


PERMISSION_HINT = ("Allow Aerox Lite in System Settings → Privacy & Security → Input Monitoring and "
                   "Accessibility, then restart the app. Macros and multi-click need both.")
