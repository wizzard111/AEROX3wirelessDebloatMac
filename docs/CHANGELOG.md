# Changelog

## V5.1.0

- **Panel animation:** a small looping drawing in the free space at the bottom of the left panel, one
  for the light theme and one for the dark, painted in the theme colours. It plays only while the
  window is open and in front (about 1% of one CPU core); with another program in front it holds
  still, and in the tray it uses no CPU and no memory for images. Hidden when the log is open or there
  is no room. Preview: `docs/images/panel-animation-preview.png`.
- **App icon:** the app in Finder, Launchpad and the Dock now shows the mouse mark of the window header
  instead of the default icon.

## V5.0.2
- Fixed: after switching from the light to the dark theme, colour swatches set to white were drawn
  dark on the Lighting tab until the app was restarted. Only swatches that show a theme colour (an
  "off" reactive colour) follow the theme now; the colours you choose never change.

### Size and resource use
- Download: AeroxLite-macos-arm64.dmg 14 MB.
- Memory and CPU are not measured on macOS yet; the same code uses 41-56 MB and about 0% CPU on
  Windows and Linux, in the tray or with the window open.

## V5.0.1

### Highlights
- **65 more SteelSeries mice.** Rival, Sensei, Prime, Aerox 5 / 9, Kana and Kinzu models (76 USB IDs)
  are recognised automatically and get the same window as the Aerox 3, with a picture of your model.
  Nothing extra to download. See "Supported mice" in the README.
- **New look** with a light and a dark theme, an interface size control and small animations.
- **Fixed on macOS:** the app no longer quits unexpectedly when you close it, turn on the mouse
  sensor log or use a macro (macOS 14 and later, including macOS 26).

### Other SteelSeries mice
- Found by their USB ID, from the open device descriptions of
  [rivalcfg](https://github.com/flozz/rivalcfg); the Aerox 3 Wireless keeps its own full-featured code.
- Window built for each model: buttons on the left, a picture of the mouse with its lit zones in your
  colours in the middle, and the Settings, Lighting and Modules tabs on the right.
- Button remapping on 47 models: another button, CPI switch, scroll, a keyboard key, a media key or a
  macro.
- CPI levels or presets, polling rate, every colour zone with "Set all", lighting effects, reactive
  colour.
- Wireless mice show the battery level and forecast and the sleep / dim timers; wired mice show a short
  summary instead.
- Settings are remembered per model and sent again on connect.

### Look and feel
- Rounded cards, switches, pill buttons and tabs, round colour swatches, an app icon, clearer button
  names (Left button -> Left click), a battery indicator and a connection chip in the header.
- Light and dark theme: the switch at the top left changes it at once; the choice is saved.
- Interface size: A- / A+ at the top right scale text, buttons and the mouse picture (50-200%, limited
  by the screen); HiDPI screens are detected.
- The window never squeezes its content: columns cannot slide over the mouse picture, and the right
  column keeps one width for all tabs.
- Activity shows the last two events; the full log opens on demand.
- Small animations, only while something changes: switches slide, the theme switch slides before the
  colours change, and a new colour fades in on the mouse picture.

### Faster and leaner
- Near-zero background cost: threads and the window sleep until something happens (idle wakeups
  ~47/s -> under 1/s); the mouse picture is redrawn only when it changes and only while visible.
- The keyboard and mouse event taps run only while a feature needs them (macros, multi-click, smart
  lighting, the visible sensor log); multi-click shares the app's listener.
- Theme and interface size change in place (theme ~0.8 s -> ~0.2 s); switching tabs takes ~20 ms.
- At login the app starts in the menu bar and builds its window only when first opened
  (~0.65 s -> ~0.1 s of start-up work).
- rivalcfg and the pictures of other mice load only when such a mouse is plugged in; one USB scan per
  check; unplugging a mouse is noticed at once.
- Smaller app: unused image codecs, colour management, OpenSSL and Tcl time-zone data are left out;
  bytecode is optimised.

### macOS
- Fixed: quitting (menu bar Quit, Cmd+Q or the power button) could end with "Aerox Lite quit
  unexpectedly". Settings are saved first, then the app exits without the Tk/Cocoa teardown that
  crashed.
- Fixed: turning on the mouse sensor log, or a macro waiting for its key, made the app quit on recent
  macOS. The macro keys F13-F20 are now read by key code only, and the keyboard that plays macros is
  prepared on the main thread.
- The sensor log is for one session: it is always off when the app starts.
- The app asks for Input Monitoring and Accessibility with the system dialogs on first launch, and
  again when a feature that needs them is turned on.
- A hard crash, if one ever happens, is written to crash.log in the app folder.

### Install and uninstall
- "Install Aerox Lite.command" for any Mac, Intel included: finds or installs Python, builds and
  checks the app, opens a drag-to-Applications window and starts the app. Releases ship a disk image
  (AeroxLite-macos-arm64.dmg).
- "Uninstall Aerox Lite.command" removes the app, its login item and its permissions, and asks whether
  to remove only the app or everything (settings and the downloaded folder too).
- HOW-TO-INSTALL.txt: a step-by-step guide, included in the download.
- The repository root and the download hold only the installer, the uninstaller and the guide.

### Smaller fixes
- When the mouse cannot be opened, the log says why (no SteelSeries device, wrong interface, or the
  exact error with a permission hint).
- Saving or deleting a macro no longer leaks the old button menus; a failing input callback no longer
  stops the listener; the SteelSeries GG check no longer delays start-up.
- Every build is self-tested before it is packaged.

## V5 — macOS edition
- First macOS release, ported from the Windows V5 edition. Same device protocol, UI and config format.
- Macro trigger keys F13–F20 and mouse input are captured with pynput (Quartz event taps); injected
  events from macros and multi-click are ignored. Playback through pynput controllers; `text` types
  any characters. Up to 8 macros (macOS has no F21–F24); `cmd` / `option` key names added.
- Menu bar icon, Dock icon click reopens the window, Cmd+Q quits cleanly, new **QUIT** button.
- Config in `~/Library/Application Support/AeroxLite`, autostart through a LaunchAgent,
  notifications via Notification Center, single-instance lock file.
- Not included: directional sensitivity (the Raw Accel driver is Windows-only).

## Windows history

### V5 — public GitHub release
- English-only: the RU/EN switch and the Russian UI were removed; all UI text, logs,
  notifications, comments and docs are in English. A `language` key left in an old
  config is ignored.
- Macro scripts: the Russian-language command aliases for `wait` and `text` were removed.
- MIT license, GitHub Actions build (tests + PyInstaller EXE, attached to tagged releases).

### V5 — optimizations
- Removed the "Everywhere / Minecraft only" choice: multi-click works in all applications.
- Removed the foreground-process check from the low-level mouse hook.
- RGB: no HID commands are sent for zones whose color did not change.
- Smart lighting: when inactive, its thread polls 4 times/s instead of 20.
- Tray preview refreshes at most once per second.
- Existing configs are kept; obsolete `only_apps` / `apps` keys are ignored.

### V5 — modules
- Fixes after the first test: the tray item toggles only multi-click and directional
  sensitivity; the "RAW ACCEL FOLDER" button searches for Raw Accel automatically first;
  the battery forecast is shown immediately (estimate) and then learns from 5% step changes.
- Modules tab: every module has its own toggle. A disabled module is not imported at
  startup and uses no resources. State is stored in %APPDATA%\AeroxLite
  (directional_state.json, rclick.json, smartbattery.json).
- Directional sensitivity: calibration mini-game (8 directions x 4 flicks, Raw Input,
  cursor confined to the window) in a separate process (`AeroxLite.exe --calibrate`,
  before the mutex) so it does not interfere with the main app's Raw Input. Applied via
  Raw Accel 1.6+: a copy of your settings.json with Output DPI, Y/X, L/R and U/D
  (→ ↓ ← ↑) is passed to writer.exe. Your settings.json is never changed; off =
  writer.exe settings.json. The profile is re-applied when Aerox Lite starts (after a
  reboot the driver loads its own settings).
- Left/right multi-click: each button has its own toggle and ×2…×6 slider; the tap
  threshold is adjustable (60–400 ms). Short press = N clicks, holding works as usual.
  The WH_MOUSE_LL hook is installed only while the module is on; physical input is never
  swallowed and injected clicks (including macros) are ignored.
- Smart battery: runtime forecast in the status bar and tray (based on actual discharge,
  PC downtime excluded). Below 25% and not charging: a "battery low" notification and a
  temporary saver (500 Hz, lighting off) without changing the config; "Save to mouse"
  during the saver writes the real settings to mouse memory. Restored on charging or ≥30%.
- Tray: one item turns the modules off and restores exactly those that were on.
- 17 new tests (36 total).
- Fixed before release: the battery forecast lost discharge segments with sparse samples.

### V4 HID padding hotfix
- Accept successful Windows HIDAPI writes padded to the output report length.
  Exact byte-count equality caused false disconnects on the Aerox dongle.
- Preserve short/zero/failed-write checks and include actual counts in errors.
- Validate probe/battery writes through the same helper.
- Add three regression tests; 19 tests now pass.

### V4 encoding hotfix
- Explicit UTF-8 in every test file read; Windows CP1251 no longer corrupts
  macro source or breaks translation checks. Build commands enable UTF-8 mode.

### V4
- RU/EN runtime switch, persisted language, translated UI/tray/editor/errors.
  An unsaved macro draft is retained when switching languages; old log lines
  and user-provided names/scripts remain in their original language.
- Validate imported config: CPI levels (1–5), active level, polling, timers,
  color strings, modes, macro slots and bindings. Unknown/invalid values
  fall back to defaults. V3 settings remain compatible.
- Atomically replace config through a temporary file, flush/fsync and replace.
  Disk errors are logged and shown rather than claiming successful saving.
- Queue immutable configuration snapshots for settings application.
  Hold the HID lock across entire apply/effect/smart-light transactions.
- Only accept battery reports matching the requested command. Bound draining
  to 64 reports per call; reject partial HID command writes and reconnect.
- Show saving-in-progress until the save command has been sent successfully.
- Persist effect speed changes. Reject adding more than five CPI levels.
- Monotonic timing, interruptible thread waits, stop Raw Input and macro test
  threads on exit; restore a static fallback for software lighting.
- Thread-safe rotating logger, capped UI queue work per tick, skip mouse art
  rendering while hidden, and redraw the tray icon only when state changes.
- Raw Input startup error reporting, synchronized sensor counters, device
  cache refresh on device changes, explicit Win32 teardown/prototypes.
- Macro parser supports tabs, text injection supports UTF-16 surrogate pairs,
  SendInput failures are reported; release partially pressed key combinations
  on errors, cancel running macros when edited/deleted.
- Windows single-instance mutex avoids concurrent controllers.
- Isolated Windows build with regression tests and proper failure handling.
- No old V3 executable/build cache included. UPX disabled in the build spec.
