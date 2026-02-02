# KLYP - A Clipboard Manager and Snippet Tool

KLYP is a lightweight, Windows-native clipboard manager and snippet tool with always-on-top sticky notes. It is designed to be a fast and low-friction way to manage a library of frequently used text snippets.

## Key Features

- **Persistent Snippet Library:** Store and manage an unlimited number of text snippets.
- **Search:** Quickly find snippets by searching through labels, tags, and content.
- **Global Hotkeys:**
    - `Ctrl+Shift+\` : Show/Hide the main clipboard window.
    - Per-snippet hotkeys for quick pasting.
- **Clipboard History:** Automatically captures text copied from other applications (configurable limit).
- **Pinning:** Pin important snippets to keep them at the top of the list.
- **Always-on-Top:** The clipboard window stays on top of other applications for easy access.
- **Quick-Paste:** Per-snippet hotkeys not only copy the content but also paste it into the active window.
- **Multi-select Delete:** Select and delete multiple snippets at once.

## Setup and Installation

This project uses a Python virtual environment.

1.  **Create the virtual environment:**
    ```shell
    python -m venv venv
    ```

2.  **Activate the virtual environment:**
    ```shell
    .\venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```shell
    pip install -r requirements.txt
    ```

## Usage

-   **Run the application:**
    ```shell
    python -m klyp.klyp_app
    ```
-   The application will run in the system tray.

## Building the Executable

To build the standalone `.exe` file, ensure PyInstaller is installed (`pip install pyinstaller`).

Then, run the following command from the project root:

```shell
pyinstaller --onefile --noconsole --name KLYP --icon=res/klyp_icon.png --add-data "res;res" klyp/klyp_app.py
```

The final `KLYP.exe` will be located in the `dist/` directory. For best results and smaller file size, it is recommended to install [UPX](https://upx.github.io/) and have it available in your system's PATH.
