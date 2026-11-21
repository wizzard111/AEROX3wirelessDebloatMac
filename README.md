# Aerox Lite for macOS

A lightweight, free replacement for SteelSeries GG on macOS. Made for the **SteelSeries Aerox 3 Wireless**
(2020 / 2022, Snow, Ghost) and now also for **65 other SteelSeries mice**: Rival, Sensei, Prime, Aerox 5 / 9,
Kana and Kinzu ([supported mice](#supported-mice)).

- **Battery** level in the menu bar and the window, with a forecast of the time left
- **CPI** levels, **polling rate**, **sleep and dim timers**
- **Buttons**: remap to another button, a key, a media key or a **macro**
- **Lighting** per zone, shown on a picture of your mouse in your colours; software effects on the Aerox 3
- **Modules**: multi-click and smart battery forecast
- Light and dark theme, interface size 50–200%, HiDPI screens
- Starts at login if you like; near-zero background cost; no account, no telemetry, no internet connection

The device protocol is based on the open-source [rivalcfg](https://github.com/flozz/rivalcfg) project.

> **Before you start:** quit SteelSeries GG and remove it from Login Items. GG overwrites the mouse lighting and settings.

## Install

> **New to this?** Follow [HOW-TO-INSTALL.txt](HOW-TO-INSTALL.txt), a simple step-by-step guide. It is also included in the download.

**Apple Silicon (M1, M2, M3, M4 …):** download `AeroxLite-macos-arm64.dmg` from **Releases**, open it and drag **Aerox Lite** onto **Applications**. On first launch, right-click the app and choose **Open**.

**Any Mac, including Intel:** download the source (**Code → Download ZIP**), unzip it and double-click **Install Aerox Lite.command**. The first time, right-click it and choose **Open**. A Terminal window shows each step:
1. It finds Python 3.10–3.14 with Tk, or offers to install the official one from python.org (your password is asked once).
2. It offers to quit SteelSeries GG.
3. It builds the app for your Mac and checks it.
4. It opens a window where you drag **Aerox Lite** into **Applications**, then starts the app.

The full log is saved as `install.log`.

**Permissions.** On first launch Aerox Lite asks macOS for **Input Monitoring** and **Accessibility**. Click **Open System Settings** in each dialog, switch Aerox Lite on, then quit and reopen the app. They are needed only for macros, multi-click and smart lighting; mouse settings, lighting and battery work without them. A rebuilt app counts as a new app, so permissions may have to be granted again after an update.

## Disk space, memory and CPU

| | |
|---|---|
| Download | `AeroxLite-macos-arm64.dmg` 14 MB |
| Settings and logs | settings a few KB; log files at most 1 MB |

Memory and CPU have not been measured on macOS yet. The same code, measured on Windows and Linux, uses
41–56 MB of memory and about 0% CPU (10–16 ms of CPU time per minute) whether it sits in the tray or
its window is open. The window is built only when you open it, and the app sleeps until something
happens (a setting, the mouse, a battery check every 30 s). Software lighting effects (breathing, wave,
colour cycle) are the exception: they keep sending colours to the mouse while they run.

## Build from source

Run `Install Aerox Lite.command`. It does everything described above.

To build by hand, you need Python 3.10–3.14 with Tk. The installer from [python.org](https://www.python.org/downloads/macos/) includes Tk.

```
PYTHON=python3.14 packaging/macos/build.sh   # .venv, dependencies, tests, "build/dist/Aerox Lite.app"
packaging/macos/make-dmg.sh                   # build/AeroxLite.dmg (drag-to-Applications window)
packaging/macos/run.sh
```

When running from source, grant the permissions to the app you start it from (Terminal, iTerm, …).

To remove the app, run **Uninstall Aerox Lite.command**. It quits and removes the app, its login item and its macOS permissions. Then it asks what else to remove:

1. **Nothing else:** only the app goes.
2. **Everything:** your settings and the downloaded folder too, including the installer and the uninstaller.

## Project layout

| Path | Contents |
|---|---|
| `Install Aerox Lite.command`, `Uninstall Aerox Lite.command` | Installer and uninstaller |
| `src/` | Application source code |
| `packaging/macos/` | PyInstaller spec, build, disk-image and run scripts |
| `packaging/requirements*.txt` | Python dependencies |
| `tests/` | Unit tests |
| `docs/CHANGELOG.md` | Version history |

## Files

| File | Location |
|---|---|
| Config | `~/Library/Application Support/AeroxLite/config.json` |
| Log | `~/Library/Application Support/AeroxLite/log.txt` (rotated at 512 KiB) |
| Autostart | `~/Library/LaunchAgents/io.github.aeroxlite.plist` (when **Start on login** is on) |

Closing the window keeps the app in the menu bar. Click the Dock icon or choose **Open** in the menu bar to bring it back. **Quit** in the menu bar, the power button at the top right or Cmd+Q exits.

Software lighting effects and macros work only while the app is running. The static color and the hardware rainbow keep working without the app after **Save to mouse**.

## Other SteelSeries mice

Aerox Lite also works with the other SteelSeries mice that [rivalcfg](https://github.com/flozz/rivalcfg) supports
(65 models, 76 USB IDs: Rival 3/5/100/110/300/310/500/600/650/700, Sensei, Prime, Aerox 5/9, Kana, Kinzu, ...; see [Supported mice](#supported-mice)).
Plug the mouse in and the app finds it by itself: nothing to download or install, the descriptions
of every supported model come with the app.

These mice get the same window as the Aerox 3, built from what each model can do:

- **Buttons** (left): remap any button to another button, CPI switch, scroll, a keyboard key, a
  media key or a **macro** (47 models; a macro is sent as one of the keys F13–F24, which the app
  turns into the macro, exactly as for the Aerox 3).
- **Picture** (centre): a drawing of your model with the parts that light up shown in the colours you
  pick, and tags (W wheel, LG logo, L1/R1 side strips, Z1 zones) that match the Lighting tab.
- **Settings**: CPI levels or presets and polling rate. A **wireless** mouse adds its battery level
  and forecast and the sleep / dim timers; a **wired** one shows a short summary instead.
- **Lighting**: every colour zone, "Set all", effects, reactive colour. **Modules** work as usual.

Changes apply at once; **Save to mouse** stores them in the mouse. Settings are remembered per model
and sent again on connect when "Apply settings on connect" is on. Software lighting effects stay an
Aerox 3 feature, and the Aerox 3 always uses its own code path.

## Supported mice

Plug the mouse in and Aerox Lite finds it by its USB ID; nothing to download or set up. The Aerox 3 Wireless
has the full feature set; the other models get every setting their device description offers.

<details>
<summary><b>All 66 models</b> (76 USB IDs) — click to open</summary>

| Model | Connection | Button remapping & macros | Colour zones | Battery | CPI |
|---|---|---|---|---|---|
| **Aerox 3 Wireless** (2020 / 2022, Snow, Ghost, CS2 Dragon Lore) | USB + 2.4 GHz | yes, plus macros | 3 + software effects | yes | 100–18000 |
| Aerox 3 | USB | yes | 3 | — | 200–8500 |
| Aerox 5 | USB | yes | 3 | — | 100–18000 |
| Aerox 5 Wireless | USB + 2.4 GHz | yes | 3 | yes | 100–18000 |
| Aerox 5 Wireless Destiny 2 Edition | USB + 2.4 GHz | yes | 3 | yes | 100–18000 |
| Aerox 5 Wireless Diablo IV Edition | USB + 2.4 GHz | yes | 3 | yes | 100–18000 |
| Aerox 9 Wireless | USB + 2.4 GHz | — | 3 | yes | 100–18000 |
| Aerox 9 Wireless WOW Edition | USB + 2.4 GHz | — | 3 | yes | 100–18000 |
| Prime | USB | yes | 1 | — | 50–18000 |
| Prime CS:GO Neo Noir Edition | USB | yes | 1 | — | 50–18000 |
| Prime Mini | USB | yes | 1 | — | 50–18000 |
| Prime Mini Wireless | USB + 2.4 GHz | yes | 1 | yes | 100–18000 |
| Prime Wireless | USB + 2.4 GHz | yes | 1 | yes | 100–18000 |
| Prime+ | USB | yes | 1 | — | 50–18000 |
| Prime Rainbow 6 Siege Black Ice Edition | USB | yes | 1 | — | 50–18000 |
| Rival | USB | yes | 2 | — | 50–6500 |
| Rival Dota 2 Edition | USB | yes | 2 | — | 50–6500 |
| Rival 3 | USB | yes | 4 | — | 200–8500 |
| Rival 3 (firmware v0.37.0.0) | USB | yes | 4 | — | 200–8500 |
| Rival 3 Gen 2 | USB | yes | 3 | — | 200–8500 |
| Rival 3 Wireless | 2.4 GHz | yes | — | yes | 100–18000 |
| Rival 3 Wireless Gen 2 | 2.4 GHz | yes | — | yes | 100–18000 |
| Rival 5 | USB | yes | 10 | — | 100–18000 |
| Rival 5 Destiny Edition | USB | yes | 10 | — | 100–18000 |
| Rival 95 | USB | — | — | — | 250–4000 |
| Rival 95 MSI Edition | USB | — | — | — | 250–4000 |
| Rival 95 PC Bang | USB | — | — | — | 250–4000 |
| Rival 100 | USB | — | 1 | — | 250–4000 |
| Rival 100 (Dell China) | USB | — | 1 | — | 250–4000 |
| Rival 100 Dota 2 Edition (Lenovo) | USB | — | 1 | — | 250–4000 |
| Rival 100 Dota 2 Edition (retail) | USB | — | 1 | — | 250–4000 |
| Rival 100 PC Bang | USB | — | — | — | 250–4000 |
| Rival 105 | USB | — | 1 | — | 250–4000 |
| Rival 106 | USB | — | 1 | — | 200–7200 |
| Rival 110 | USB | — | 1 | — | 200–7200 |
| Rival 300 | USB | yes | 2 | — | 50–6500 |
| Rival 300 Acer Predator Edition | USB | yes | 2 | — | 50–6500 |
| Rival 300 CS:GO Fade Edition | USB | yes | 2 | — | 50–6500 |
| Rival 300 CS:GO Fade Edition (stm32) | USB | yes | 2 | — | 50–6500 |
| Rival 300 CS:GO Hyper Beast Edition | USB | yes | 2 | — | 50–6500 |
| Rival 300 Evil Geniuses Edition | USB | yes | 2 | — | 50–6500 |
| Rival 300 Fallout 4 Edition | USB | yes | 2 | — | 50–6500 |
| Rival 300 HP OMEN Edition | USB | yes | 2 | — | 50–6500 |
| Rival 300S | USB | — | 1 | — | 200–7200 |
| Rival 310 | USB | yes | 2 | — | 100–12000 |
| Rival 310 CS:GO Howl Edition | USB | yes | 2 | — | 100–12000 |
| Rival 310 PUBG Edition | USB | yes | 2 | — | 100–12000 |
| Rival 500 | USB | yes | 2 | — | 100–12000 |
| Rival 600 | USB | yes | 8 | — | 100–12000 |
| Rival 600 Dota 2 Edition | USB | yes | 8 | — | 100–12000 |
| Rival 650 Wireless | USB + 2.4 GHz | yes | — | yes | 100–12000 |
| Rival 700 | USB | — | 2 | — | 100–12000 |
| Rival 710 | USB | — | 2 | — | 100–12000 |
| Sensei TEN | USB | yes | 2 | — | 50–18000 |
| Sensei TEN CS:GO Neon Rider Edition | USB | yes | 2 | — | 50–18000 |
| Sensei [RAW] | USB | yes | — | — | 90–5670 |
| Sensei [RAW] CoD Black Ops II Edition | USB | yes | — | — | 90–5670 |
| Sensei [RAW] Diablo III Edition | USB | yes | — | — | 90–5670 |
| Sensei [RAW] Heroes of the Storm Edition | USB | yes | — | — | 90–5670 |
| Sensei [RAW] World of Tanks Edition | USB | yes | — | — | 90–5670 |
| Sensei [RAW] Guild Wars 2 Edition | USB | yes | — | — | 90–5670 |
| Sensei 310 | USB | yes | 2 | — | 100–12000 |
| Kana v2 | USB | — | — | — | 400–4000 |
| Kinzu v2 | USB | — | — | — | 400–3200 |

</details>

"Button remapping & macros: —" means the mouse does not let its buttons be remapped from a computer
program. Colour zones are the parts that light up and can be given a colour. The device descriptions come
from [rivalcfg](https://github.com/flozz/rivalcfg); a model added there can be added here too.

## Light and dark theme

The switch at the top left (moon / sun) changes between the dark and the light look. The choice is saved.

## Interface size

Use **A−** and **A+** at the top right of the window to make text, buttons and the mouse picture smaller or larger (50%–200%, limited by the screen size). The choice is saved.

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
git tag v5.0.2
git push origin v5.0.2
```

The workflow runs the tests, builds the app on Apple Silicon, self-tests it and attaches `AeroxLite-macos-arm64.dmg` to a GitHub Release.

## Disclaimer

This is an unofficial project, not affiliated with or endorsed by SteelSeries. "SteelSeries" and "Aerox" are trademarks of their respective owners. Use at your own risk.

## License

[MIT](LICENSE). The bundled app also contains third-party libraries under their own licenses: [hidapi](https://github.com/trezor/cython-hidapi) (BSD option), [rivalcfg](https://github.com/flozz/rivalcfg) (WTFPL, mouse descriptions), [pynput](https://github.com/moses-palmer/pynput) (LGPL-3.0), [pystray](https://github.com/moses-palmer/pystray) (LGPL-3.0), [Pillow](https://github.com/python-pillow/Pillow) (MIT-CMU), [PyObjC](https://github.com/ronaldoussoren/pyobjc) (MIT), and [PyInstaller](https://pyinstaller.org) bootloader (GPL with a bundling exception).
