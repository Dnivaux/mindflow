"""
MindFlow Markdown — main.py
Architecture: JS-driven Markmap (no node/npx dependencies).
Python handles only PyWebView and native File Dialogs.

FIXES:
- Removed Tkinter (thread-unsafe) → Using PowerShell COM (native Windows)
- Fixed sys._MEIPASS path handling → Direct file:// URL construction
- Added robust logging for .exe debugging
"""

import webview
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from threading import Lock

# ── Logging Setup (critical for .exe debugging) ────────────────────────────────
def _setup_logging():
    """Setup logging to file (visible from .exe even with console=False)."""
    if getattr(sys, 'frozen', False):
        # .exe runs from dist folder
        log_dir = os.path.join(os.path.expanduser('~'), '.mindflow')
    else:
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.logs')

    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'mindflow.log')

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(),  # Also to console (visible during debug=True)
        ]
    )
    logging.info(f"Logging initialized. Log file: {log_file}")
    return logging.getLogger(__name__)

logger = _setup_logging()

# ── Paths ────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    logger.info(f"Running as .exe (frozen). BASE_DIR = {BASE_DIR}")
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logger.info(f"Running as script. BASE_DIR = {BASE_DIR}")

ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
INDEX_PATH = os.path.join(ASSETS_DIR, 'index.html')

logger.info(f"ASSETS_DIR = {ASSETS_DIR}")
logger.info(f"INDEX_PATH = {INDEX_PATH}")
logger.info(f"INDEX_PATH exists: {os.path.exists(INDEX_PATH)}")

SAMPLE_MD = """\
# MindFlow Markdown

## 📝 Fonctionnalités
### Édition en temps réel
### Zoom & navigation
### Repliage des nœuds

## 📤 Exports
### SVG vectoriel
### HTML autonome

## ⌨️ Raccourcis
### Ctrl+O — Ouvrir
### Ctrl+F — Ajuster la vue
"""

# ── Native Windows File Dialogs via PowerShell COM ─────────────────────────────
_dialog_lock = Lock()  # Prevent concurrent dialogs

def _powershell_open_dialog(title: str = "Open File", filters: str = "All files (*.*)|*.*") -> str | None:
    """
    Open a file dialog using PowerShell's native COM interface.
    Avoids Tkinter threading issues completely.

    Args:
        title: Dialog title
        filters: File type filters (e.g., "Markdown (*.md)|*.md|All files (*.*)|*.*")

    Returns:
        Selected file path or None if cancelled
    """
    try:
        with _dialog_lock:
            ps_script = f"""
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
$file_dialog = New-Object System.Windows.Forms.OpenFileDialog
$file_dialog.Title = "{title}"
$file_dialog.Filter = "{filters}"
$file_dialog.InitialDirectory = [Environment]::GetFolderPath("MyDocuments")
if ($file_dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {{
    Write-Host "$($file_dialog.FileName)"
}}
"""
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0 and result.stdout.strip():
                filepath = result.stdout.strip()
                logger.info(f"User selected: {filepath}")
                return filepath
            else:
                logger.info("User cancelled file dialog")
                return None
    except Exception as e:
        logger.error(f"PowerShell file dialog error: {e}")
        return None

def _powershell_save_dialog(title: str = "Save File", default_name: str = "file", filters: str = "All files (*.*)|*.*") -> str | None:
    """
    Save a file dialog using PowerShell's native COM interface.

    Args:
        title: Dialog title
        default_name: Default filename (without extension)
        filters: File type filters

    Returns:
        Selected file path or None if cancelled
    """
    try:
        with _dialog_lock:
            ps_script = f"""
[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null
$file_dialog = New-Object System.Windows.Forms.SaveFileDialog
$file_dialog.Title = "{title}"
$file_dialog.FileName = "{default_name}"
$file_dialog.Filter = "{filters}"
$file_dialog.InitialDirectory = [Environment]::GetFolderPath("MyDocuments")
if ($file_dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {{
    Write-Host "$($file_dialog.FileName)"
}}
"""
            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            if result.returncode == 0 and result.stdout.strip():
                filepath = result.stdout.strip()
                logger.info(f"User save location: {filepath}")
                return filepath
            else:
                logger.info("User cancelled save dialog")
                return None
    except Exception as e:
        logger.error(f"PowerShell save dialog error: {e}")
        return None

# ── Python API ────────────────────────────────────────────────────────────────
class Api:
    def open_file_dialog(self) -> str | None:
        """Open Markdown file with native Windows dialog."""
        logger.info("open_file_dialog() called from JS")
        try:
            filters = "Markdown files (*.md *.markdown)|*.md;*.markdown|All files (*.*)|*.*"
            filepath = _powershell_open_dialog(
                title="Ouvrir un fichier Markdown",
                filters=filters
            )
            if filepath:
                logger.info(f"Reading file: {filepath}")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        logger.info(f"File read successfully ({len(content)} chars)")
                        return content
                except Exception as e:
                    logger.error(f"Failed to read file: {e}")
                    return '__ERROR__'
            return None
        except Exception as e:
            logger.error(f"open_file_dialog exception: {e}")
            return '__ERROR__'

    def save_file_dialog(self, content: str, extension: str) -> bool | str:
        """Save content to file with native Windows dialog."""
        logger.info(f"save_file_dialog() called with extension: {extension}")
        try:
            if extension == 'svg':
                filters = "SVG files (*.svg)|*.svg|All files (*.*)|*.*"
                default_name = "mindmap"
            else:
                filters = "HTML files (*.html)|*.html|All files (*.*)|*.*"
                default_name = "mindmap"

            filepath = _powershell_save_dialog(
                title="Enregistrer la carte mentale",
                default_name=default_name,
                filters=filters
            )
            if filepath:
                logger.info(f"Saving to: {filepath}")
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info(f"File saved successfully ({len(content)} chars)")
                    return True
                except Exception as e:
                    logger.error(f"Failed to save file: {e}")
                    return str(e)
            logger.info("Save cancelled by user")
            return False
        except Exception as e:
            logger.error(f"save_file_dialog exception: {e}")
            return str(e)

    def get_vendor_scripts(self) -> dict | None:
        """Read vendor JS files and return their contents for offline HTML export."""
        logger.debug("get_vendor_scripts() called")
        vendor_dir = os.path.join(ASSETS_DIR, 'vendor')
        files = {
            'd3':          os.path.join(vendor_dir, 'd3.min.js'),
            'markmap_lib': os.path.join(vendor_dir, 'markmap-lib.umd.js'),
            'markmap_view': os.path.join(vendor_dir, 'index.js'),
        }
        result = {}
        for key, path in files.items():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    result[key] = f.read()
                logger.debug(f"Vendor loaded: {os.path.basename(path)} ({len(result[key])} chars)")
            except Exception as e:
                logger.error(f"Failed to read vendor {path}: {e}")
                return None
        return result

    def get_sample(self) -> str:
        """Return sample Markdown content."""
        logger.debug("get_sample() called")
        return SAMPLE_MD

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    logger.info("=" * 80)
    logger.info("MindFlow Markdown Application Starting")
    logger.info("=" * 80)

    try:
        api = Api()

        # SECURE: Convert absolute path to file:// URL safely
        # On Windows, use pathlib for robust path handling
        index_path = Path(INDEX_PATH).resolve()
        if not index_path.exists():
            logger.error(f"CRITICAL: index.html not found at {index_path}")
            logger.error(f"Contents of {ASSETS_DIR}:")
            if os.path.exists(ASSETS_DIR):
                logger.error(os.listdir(ASSETS_DIR))
            sys.exit(1)

        # Convert to file:// URL (PyWebView handles both on Windows)
        # Method 1: Direct path (PyWebView-recommended for Windows)
        url = str(index_path)
        logger.info(f"Loading URL: {url}")

        logger.info("Creating PyWebView window...")
        window = webview.create_window(
            title='MindFlow Markdown',
            url=url,  # PyWebView accepts absolute paths directly on Windows
            js_api=api,
            width=1280,
            height=780,
            min_size=(800, 500),
            background_color='#FFFFFF',
            text_select=True,
        )

        logger.info("Starting webview...")
        webview.start(debug=False)  # Keep False for production

    except Exception as e:
        logger.exception(f"FATAL: {e}")
        sys.exit(1)
    finally:
        logger.info("MindFlow Markdown Application Shutting Down")
        logger.info("=" * 80)

