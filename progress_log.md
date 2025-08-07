# AI Launcher Development Log

This log tracks the progress of developing the AI Launcher application.

## Initial Setup and Basic Window

- **Goal:** Create a minimal, transparent, borderless GTK window.
- **Actions:**
    - Created `ai-launcher` directory.
    - Created `main.py` with basic GTK window setup (borderless, opacity).
    - Initial window had a `Gtk.Label` for history and a `Gtk.Entry` for input.
- **Issues:**
    - Initial `write_file` command used a relative path, causing an error. Corrected to use absolute path.
    - `sudo apt-get install -y python3-gi` was required for GTK Python bindings. User performed this manually.

## Refinement: Vertical Expansion and ListBox for History

- **Goal:** Make the window expand vertically with conversation, use a `Gtk.ListBox` for better history management.
- **Actions:**
    - Modified `main.py` to use `Gtk.ListBox` for chat history.
    - Implemented `add_message` function to append new messages to the `ListBox`.
    - Set initial window size to be smaller, with the intention of dynamic resizing.

## Gemini API Integration

- **Goal:** Connect the application to the Google Gemini API.
- **Actions:**
    - Attempted `pip install google-generativeai`.
- **Issues:**
    - `pip` installation failed due to `externally-managed-environment` error.
    - Decided to use a virtual environment to manage Python dependencies.
    - Created `venv` using `python3 -m venv ai-launcher/venv`.
    - Successfully installed `google-generativeai` into the virtual environment.
    - Modified `main.py` to import `google.generativeai` and use `genai.GenerativeModel`.
    - Added placeholder for API key.
- **API Key Handling Refinement:**
    - **Goal:** Securely handle API key and create a distributable project.
    - **Actions:**
        - Removed old `venv`.
        - Created `requirements.txt` (initially `google-generativeai`, later added `python-dotenv`).
        - Created `.gitignore` to exclude `venv/` and `.env`.
        - Created `.env.example` for API key placeholder.
        - Modified `main.py` to load API key from `.env` using `python-dotenv`.
        - Created `install.sh` script to automate system dependency installation, virtual environment creation (with `--system-site-packages`), and Python package installation.
        - Made `install.sh` executable.
- **Issues during API Integration:**
    - `ModuleNotFoundError: No module named 'gi'` when running from `venv`.
    - Attempted `pip install PyGObject` in `venv`.
    - `PyGObject` installation failed due to missing `cairo` development files. User installed `libcairo2-dev pkg-config`.
    - `PyGObject` installation failed again due to missing `girepository-2.0`. User installed `libgirepository1.0-dev`.
    - `PyGObject` installation finally succeeded after all system dependencies were met.
    - Initial `run_shell_command` with `directory` parameter failed. Switched to `cd ai-launcher && ...` for execution.
    - `NotFound: 404 models/gemini-pro is not found` error from Gemini API. Corrected model name to `gemini-1.5-flash-latest`. (Initially tried `gemini-2.5-flash` which was also not found).

## UI/UX Enhancements (Single Box, Auto-Close, Auto-Resize)

- **Goal:** Implement a single `Gtk.TextView` for input/output, black 90% opacity, auto-expand downwards, auto-close on focus loss, immediate typing.
- **Actions:**
    - Rewrote `main.py` to use a single `Gtk.TextView`.
    - Implemented GTK CSS for styling (black background, white text, transparency).
    - Added `focus-out-event` handler for auto-closing.
    - Implemented `on_key_press` to capture Enter and send messages.
    - Added `insert_prompt` to manage the user input prompt.
    - Implemented `resize_window` to dynamically adjust window height and position for downward expansion.
- **Issues during UI/UX Enhancements:**
    - `AttributeError: 'gi.repository.Gdk' object has no attribute 'Pango'` due to incorrect `Pango` import. Corrected `from gi.repository import Pango` and updated tag creation.
    - AI not responding, no error in terminal. Added extensive `print("DEBUG: ...")` statements to trace execution.
    - Debugging revealed `user_text` was empty because `editable_mark` logic was flawed.
    - Replaced `Gtk.TextMark` logic with a simpler `self.input_start_offset` variable to track the start of user input. This resolved the input capture issue.

## Recent Refinements and Scrollbar Issues

- **Goal:** Improve visual consistency, update API model, and hide scrollbar.
- **Actions:**
    - Refactored `main.py` to use a `Config` class for centralized configuration.
    - Improved error handling for Gemini API calls, displaying errors in red.
    - Updated Gemini model to `gemini-2.5-flash`.
    - Changed AI response text color to white for uniformity.
    - Attempted vertical centering of initial text using `set_justification` (horizontal only, reverted).
    - Attempted vertical centering using `Gtk.Box` (broke scrolling and height limit, reverted).
    - Attempted vertical centering using `textview.set_top_margin(12)` (successful for initial centering, but scrollbar still visible).
    - Attempted to hide scrollbar using CSS with `.no-scrollbar` class (unsuccessful).
    - Attempted to hide scrollbar using `scrolled_window.set_overlay_scrolling(True)` (scrollbar still visible when content overflows).
    - Attempted to hide scrollbar by setting `Gtk.PolicyType.NEVER` in `on_size_allocated` (lost 400px limit and scrolling functionality, reverted).
- **Current Status:** The application is functional with a 400px height limit and scrolling, but the scrollbar remains visible when content overflows. The `main.py` file has been reverted to a stable, working state (`main.py.perfect.bak`).

## Final Touches

- **Goal:** Clean up debugging statements.
- **Actions:**
    - Removed all `print("DEBUG: ...")` statements from `main.py`.

## Performance, UI, and Web Search Investigation

- **Goal:** Address UI bugs, improve performance, and enable web search.
- **Actions:**
    - **UI Cropping:** Replaced manual height calculation with a more accurate method (`vadjustment.get_upper()`) to prevent text from being cut off.
    - **Performance:** Implemented streaming responses (`chat.send_message(stream=True)`) to make the application feel more responsive by displaying text as it's generated.
    - **Scrolling:** Changed the scroll behavior to keep the view at the top of the AI's response, rather than automatically scrolling to the end.
    - **Web Search:**
        - Attempted to enable the built-in `GoogleSearch` tool based on online documentation.
        - Encountered a series of `ImportError` and `AttributeError` issues, indicating a mismatch between the documentation and the installed `google-generativeai` library version (`0.8.5`).
        - Inspected the library's modules directly to confirm that the web search tool is not available in the installed version.
        - Attempted to upgrade the library via `requirements.txt`, but discovered that no newer stable version with the feature is available on PyPI.
        - Reverted all code changes related to web search to ensure application stability.

## Command and UI Adjustments

- **Goal:** Add application shortcuts and adjust window layout.
- **Actions:**
    - Implemented a `handle_command` method to process user commands.
    - Added commands to open the default browser (`/b`), file manager (`/f`), and terminal (`/t`). Used `x-www-browser`, `thunar`, and `xfce4-terminal` for Xubuntu compatibility.
    - Modified the `Config` class to increase `MAX_HEIGHT` from 400 to 800.
    - Changed the window positioning logic to place the launcher 25% from the top of the screen instead of centered.

## Current Status

The AI Launcher application is fully functional. All known UI bugs have been addressed, and performance has been improved. The web search feature could not be implemented due to library limitations.

- **Features:**
    - Single, borderless, transparent window.
    - Auto-closes on focus loss.
    - Auto-expands vertically with conversation history, up to a 800px limit.
    - Window appears 25% from the top of the screen.
    - Uses a single `Gtk.TextView` for input and output.
    - Securely handles API key via `.env` file.
    - Provides an `install.sh` script for easy setup.
    - Displays API errors gracefully.
    - Resets for new queries after a conversation is complete.
    - Scrollbar appears only when needed.
    - Up and Down arrow keys control scrolling when the scrollbar is visible.
    - AI responses stream in for better perceived performance.
    - View stays at the top of long responses by default.
    - Shortcuts `/b`, `/f`, and `/t` to launch external applications.
- **Known Issues:**
    - Built-in web search is not available due to limitations in the current stable version of the `google-generativeai` library.
- **Next Steps:**
    - Ready for user testing and feedback.