# Aerox Lite for macOS

A lightweight replacement for SteelSeries GG for the **SteelSeries Aerox 3 Wireless** (2020/2022, Snow/Ghost) on macOS.

Features: battery level (menu bar and window), CPI levels, polling rate, sleep/dim timers, button bindings, lighting (including software effects), macros, multi-click and smart battery.

The device protocol is based on the open-source [rivalcfg](https://github.com/flozz/rivalcfg) project.

> **Before you start:** quit SteelSeries GG and remove it from Login Items. GG overwrites the mouse lighting and settings.

## Install

> **New to this?** Follow [HOW-TO-INSTALL.txt](HOW-TO-INSTALL.txt), a simple step-by-step guide. It is also included in the download.

1. Download `AeroxLite-macos-arm64.zip` from **Releases** (Apple Silicon), unzip it and move **Aerox Lite.app** to Applications.
2. The app is not notarized by Apple. On first launch, right-click it and choose **Open**, then confirm. If macOS still blocks it, open **System Settings → Privacy & Security** and click **Open Anyway**.
3. For macros, multi-click and smart lighting, allow Aerox Lite in **System Settings → Privacy & Security** under both **Input Monitoring** and **Accessibility**, then restart the app.

Mouse settings, lighting and battery work without these permissions.

On an Intel Mac, build from source (below).

## Build from source

Requires Python 3.10+ with Tk. The installer from [python.org](https://www.python.org/downloads/macos/) includes Tk. With Homebrew, run `brew install python python-tk`.

```
./build.sh   # creates .venv, installs dependencies, runs the tests, builds "dist/Aerox Lite.app"
./run.sh
```

When running from source, grant the permissions to the app you start it from (Terminal, iTerm, …).

## Files

| File | Location |
|---|---|
| Config | `~/Library/Application Support/AeroxLite/config.json` |
| Log | `~/Library/Application Support/AeroxLite/log.txt` (rotated at 512 KiB) |
| Autostart | `~/Library/LaunchAgents/io.github.aeroxlite.plist` (when **Start on login** is on) |

Closing the window keeps the app in the menu bar. Click the Dock icon or choose **Open** in the menu bar to bring it back. **Quit** in the menu bar, the **QUIT** button or Cmd+Q exits.

Software lighting effects and macros work only while the app is running. The static color and the hardware rainbow keep working without the app after **Save to mouse**.

## Modules

Each module on the **Modules** tab has its own toggle. Disabled modules are not loaded.

- **Multi-click (left / right)**: each button has its own toggle and a ×2…×6 slider. A press shorter than the tap threshold (60–400 ms) sends multiple clicks; a longer press is a normal hold.
- **Smart battery**: shows a runtime forecast. Below 25%, you get a notification and a temporary power saver (500 Hz, lighting off). Everything is restored when charging or at ≥30%.

Directional sensitivity from the Windows edition is not available. It relies on the Raw Accel driver, which exists only for Windows.

## Macros

A mouse button bound to a macro sends one of the keys F13–F20. macOS has no F21–F24, so **up to 8 macros** are available. One action per line:

```
ctrl+c        key combination (use cmd+c for the usual macOS shortcut)
enter         single key
down shift    hold key
up shift      release key
wait 50       delay, ms
text Hello    type text (any characters)
click left    left / right / middle click
# ...         comment
```

`win` and `cmd` both mean the Command key; `alt` and `option` both mean Option.

Assign a macro to a mouse button under **Actions → Macros**.

## macOS limitations

- macOS does not report which device an event came from. Multi-click and smart lighting react to every mouse and the trackpad. F13–F20 pressed on a keyboard also trigger macros.
- `printscreen` is not available as a macro key.

## Development

```
python3 -X utf8 -m unittest discover -s tests -v
```

### Releasing

```
git tag v5.0.0
git push origin v5.0.0
```

The workflow runs the tests, builds the app on Apple Silicon and attaches `AeroxLite-macos-arm64.zip` to a GitHub Release.

## Disclaimer

This is an unofficial project, not affiliated with or endorsed by SteelSeries. "SteelSeries" and "Aerox" are trademarks of their respective owners. Use at your own risk.

## License

[MIT](LICENSE). The bundled app also contains third-party libraries under their own licenses: [hidapi](https://github.com/trezor/cython-hidapi) (BSD option), [pynput](https://github.com/moses-palmer/pynput) (LGPL-3.0), [pystray](https://github.com/moses-palmer/pystray) (LGPL-3.0), [Pillow](https://github.com/python-pillow/Pillow) (MIT-CMU), [PyObjC](https://github.com/ronaldoussoren/pyobjc) (MIT), and [PyInstaller](https://pyinstaller.org) bootloader (GPL with a bundling exception).
