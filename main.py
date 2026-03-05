"""
MindFlow Markdown — main.py
Architecture: JS-driven Markmap (no node/npx dependencies). 
Python handles only PyWebView and native File Dialogs.
"""

import webview
import os
import sys
import tkinter as tk
from tkinter import filedialog

# ── Paths ────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ASSETS_DIR  = os.path.join(BASE_DIR, 'assets')

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

def _tk_dialog(fn):
    """Run a tkinter dialog in a temporary hidden root (thread-safe)."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    try:
        return fn(root)
    finally:
        root.destroy()

# ── Python API ────────────────────────────────────────────────────────────────
class Api:
    def open_file_dialog(self) -> str | None:
        def ask(root):
            return filedialog.askopenfilename(
                parent=root,
                title='Ouvrir un fichier Markdown',
                filetypes=[('Markdown', '*.md *.markdown'), ('Tous', '*.*')],
            )
        filepath = _tk_dialog(ask)
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                return '__ERROR__'
        return None

    def save_file_dialog(self, content: str, extension: str) -> bool | str:
        if extension == 'svg':
            filetypes = [('SVG', '*.svg')]
            default_name = 'mindmap.svg'
        else:
            filetypes = [('HTML', '*.html')]
            default_name = 'mindmap.html'

        def ask(root):
            return filedialog.asksaveasfilename(
                parent=root,
                title='Enregistrer sous',
                initialfile=default_name,
                defaultextension=f'.{extension}',
                filetypes=filetypes,
            )
        filepath = _tk_dialog(ask)
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                return str(e)
        return False

    def get_sample(self) -> str:
        return SAMPLE_MD

# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    api = Api()

    index_path = os.path.join(ASSETS_DIR, 'index.html')
    index_url  = 'file:///' + index_path.replace(os.sep, '/')

    window = webview.create_window(
        title='MindFlow Markdown',
        url=index_url,
        js_api=api,
        width=1280,
        height=780,
        min_size=(800, 500),
        background_color='#FFFFFF',
        text_select=True,
    )

    webview.start(debug=False)

