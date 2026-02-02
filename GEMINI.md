You are a senior Windows desktop engineer. Design and implement a standalone Windows .exe in Python that replicates and improves Ditto.

Goal
I need a “persistent clipboard + snippet library” for 5–50 long text snippets that I reuse daily. It must have reliable global hotkeys, visible labels (names) in the list, and the ability to pin any snippet as an always-on-top sticky note on the desktop.

Name of application/software
KLYP

Hard requirements
1) Windows 11 native app feel, fast, low friction.
2) Standalone .exe output (PyInstaller or equivalent). No external runtime installs.
3) Unlimited snippet length (no tiny character limits).
4) Each snippet has:
   - Visible label/title (not included in pasted text)
   - Content (what gets pasted)
   - Optional tags (comma-separated)
   - Optional group/folder (e.g., “Daily”, “Work”, “Jira”)
5) Global hotkeys must be reliable and deterministic:
   - Hotkey opens the clipboard window (default: Ctrl+`)
   - Per-snippet hotkeys paste that exact snippet (e.g., Ctrl+Alt+1..9)
   - Hotkeys must not “randomly paste the wrong one”
   - Provide a hotkey conflict detector and UI warning
6) Clipboard window:
   - Shows label/title prominently (NOT the first line of content)
   - Search box that searches title/tags/content
   - Keyboard navigation: up/down, Enter paste, Esc close
   - “Pinned” section at the top
   - Quick edit: rename, edit content, change hotkey, pin/unpin
7) Sticky note pins:
   - From clipboard window, you can drag any snippet out onto the desktop as a sticky note
   - Sticky note shows: title + (optionally) a preview; click to copy/paste
   - Sticky notes are Always-on-Top
   - Sticky notes can be resized, moved, color-coded, and persist across restarts
   - Sticky note has controls: Copy, Paste into active app, Edit, Close (remove pin)
8) Persistence:
   - Snippets persist across reboots, stored locally in a sqlite database (or robust local storage)
   - Sticky note positions/sizes/colors persist across reboots
   - Optional encryption-at-rest toggle (for sensitive snippets)
9) Tray app behavior:
   - Runs in system tray
   - Right-click menu: Open, Settings, Pause Hotkeys, Quit
   - Start with Windows option
10) Paste behavior:
   - “Paste into active app” should work even if the clipboard content is large
   - Support multiple paste modes: set clipboard + send Ctrl+V; or direct send input where appropriate
   - Provide fallback logic when an app blocks one method
11) Import/Export:
   - Export all snippets to JSON
   - Import from JSON
   - Backup/restore
12) Reliability + debuggability:
   - Logging to a local file
   - “Diagnostics” screen: registered hotkeys, conflicts, last errors
13) Performance:
   - Opens instantly (<200ms target on normal PC)
   - Does not leak memory
   - Minimal CPU when idle

Nice-to-have features (include if reasonable)
- Clipboard history capture (optional toggle). If enabled:
  - capture last N clipboard entries (text only at first)
  - allow promoting a history item to a named snippet
- Snippet templating:
  - optional variables (date/time, username) with a safe, simple syntax
- Multi-monitor sticky notes support
- Quick paste menu that appears near cursor
- Per-snippet “paste as plain text” toggle
- Per-snippet “auto-append newline” toggle

Tech stack constraints
- Python 3.11+
- Use PySide6 (Qt) for UI (preferred), or PyQt6 if needed
- Use a mature global hotkeys library that works well on Windows 11
- Use Windows APIs where necessary for focus/active window paste behavior
- Packaging: PyInstaller onefile (or onefolder if onefile causes issues), include icons
- No web services required, offline app
- The project MUST create and use a Python virtual environment (venv) located in the project root folder.
- All dependencies MUST be installed into this venv only.
- No packages may be installed into or rely on the system Python or any existing global/user environment.
- All build and run instructions MUST explicitly activate and use this local venv to avoid contaminating the default Python environment.

Deliverables
A) A short design doc first:
   - Architecture (modules/classes)
   - Data model schema
   - Hotkey strategy (how you guarantee no collisions + deterministic mapping)
   - Paste strategy (how you paste reliably across apps)
   - Sticky note implementation approach
B) Then implement:
   - Project structure (folders/files)
   - Requirements.txt / pyproject.toml
   - Main app + tray + clipboard window + sticky note windows
   - SQLite storage layer + migrations
   - Settings UI
   - Import/export
   - Logging/diagnostics
C) Provide build instructions:
   - How to create the venv in the project root
   - How to activate the venv
   - How to install dependencies into the venv
   - How to build the .exe with PyInstaller using the venv
   - How to test global hotkeys (including admin privilege caveats)
D) Provide acceptance tests:
   - A checklist of manual tests that prove it meets the requirements
   - Include a “hotkey reliability test” scenario with 10 snippets

Important implementation notes
- Titles/labels must be visible in the clipboard window list; do not rely on tooltips.
- Hotkeys must map to a specific snippet ID stored in the database, not “list position”.
- Sticky note pins must not be tied to clipboard history order; they are their own persistent objects.
- Do not implement anything dangerous; do not capture passwords without user intent. Provide an opt-in “sensitive mode” and a clear warning.
- The result should be usable by a non-developer once built.

Start by writing the design doc, then proceed to implementation.
