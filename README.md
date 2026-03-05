# MindFlow Markdown

> Application desktop minimaliste qui convertit du Markdown en Mind Map interactive.

![screenshot](assets/screenshot.png)  
*(capture générée au premier lancement)*

---

## 🚀 Installation des dépendances

Assurez-vous d'avoir **Python 3.9+** installé, puis exécutez :

```bash
pip install pywebview
```

> **Note** : Sur Windows, PyWebView utilise le moteur de rendu **Edge WebView2** (pré-installé sur Windows 10/11). Si WebView2 n'est pas disponible, installez-le depuis [Microsoft Edge WebView2](https://developer.microsoft.com/fr-fr/microsoft-edge/webview2/).

---

## ▶️ Lancer l'application (mode développement)

```bash
python main.py
```

---

## 📦 Créer le fichier .exe (packaging)

### Étape 1 — Installer PyInstaller

```bash
pip install pyinstaller
```

### Étape 2 — Créer l'exécutable

Depuis le dossier racine du projet :

```bash
pyinstaller mindflow.spec
```

Le fichier `MindFlow.exe` sera généré dans le dossier `dist/`.

> **Astuce** : Si vous souhaitez ajouter une icône personnalisée, placez un fichier `icon.ico` dans le dossier `assets/` et décommentez la ligne `# icon=...` dans `mindflow.spec`.

---

## 📂 Structure du projet

```
markmap/
├── main.py            ← Point d'entrée Python (PyWebView)
├── mindflow.spec      ← Configuration PyInstaller
├── README.md
└── assets/
    ├── index.html     ← Interface utilisateur
    ├── style.css      ← Styles (thème blanc minimaliste)
    └── app.js         ← Logique Markmap + exports
```

---

## ⌨️ Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+O`  | Ouvrir un fichier `.md` |
| `Ctrl+F`  | Ajuster la vue (fit) |

---

## 📤 Exports disponibles

| Format | Description |
|--------|-------------|
| **SVG** | Image vectorielle statique |
| **HTML** | Fichier HTML autonome et interactif (fonctionne hors ligne) |
