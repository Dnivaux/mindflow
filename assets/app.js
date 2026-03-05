/**
 * MindFlow Markdown — app.js (v3)
 * Architecture: 100% Client-Side JS using window.markmap.
 */

/* ═══ Safety guard — catch missing Markmap library ══════════════════════ */
if (!window.markmap) {
  document.body.innerHTML = `
    <div style="font-family:sans-serif;padding:40px;color:#991b1b;background:#fef2f2;height:100vh;
                display:flex;flex-direction:column;align-items:center;justify-content:center;
                gap:16px;text-align:center">
      <strong style="font-size:18px">⚠️ Erreur de chargement</strong>
      <p>Les bibliothèques Markmap n'ont pas pu être chargées.<br>
         Vérifiez que les fichiers <code>assets/vendor/</code> existent et relancez l'application.</p>
    </div>`;
  throw new Error('window.markmap is undefined — vendor scripts not loaded');
}

/* ═══ Globals ═══════════════════════════════════════════════════════════ */
const { Transformer, Markmap, loadCSS, loadJS } = window.markmap;
const transformer = new Transformer();
let mm = null;   // Markmap instance

/* ═══ DOM refs ════════════════════════════════════════════════════════════ */
const textarea = document.getElementById('markdown-input');
const charCount = document.getElementById('char-count');
const svgEl = document.getElementById('mindmap-svg');
const emptyState = document.getElementById('empty-state');
const spinner = document.getElementById('spinner');
const controls = document.getElementById('controls-overlay');
const notifEl = document.getElementById('notification');
const notifText = document.getElementById('notification-text');
const notifIcon = document.getElementById('notification-icon');
const notifClose = document.getElementById('notification-close');

/* ═══ Notification ════════════════════════════════════════════════════════ */
const ICONS = { info: 'ℹ️', success: '✅', error: '⚠️' };

function showNotif(msg, type = 'info', duration = 4000) {
  notifText.textContent = msg;
  notifIcon.textContent = ICONS[type] ?? 'ℹ️';
  notifEl.className = `show ${type}`;
  clearTimeout(notifEl._t);
  if (duration > 0) notifEl._t = setTimeout(hideNotif, duration);
}
function hideNotif() { notifEl.className = ''; }
notifClose.addEventListener('click', hideNotif);

/* ═══ State ═══════════════════════════════════════════════════════════════ */
let debounceTimer = null;
const DEBOUNCE_MS = 250;

/* ═══ Render via Markmap JS ═══════════════════════════════════════════════ */
function renderMindmap() {
  const md = textarea.value.trim();

  if (!md) {
    showEmpty();
    return;
  }

  showSpinner();

  try {
    const { root, features } = transformer.transform(md);
    const { styles, scripts } = transformer.getUsedAssets(features);

    // Load necessary Markmap assets (like KaTeX, highlight.js if used)
    if (styles) loadCSS(styles);
    if (scripts) loadJS(scripts, { getMarkmap: () => window.markmap });

    if (!mm) {
      // Initialize first time — default Markmap color palette
      mm = Markmap.create(svgEl, {
        paddingX: 16,
        autoFit: true,
      }, root);
    } else {
      // Update existing map
      mm.setData(root);
      mm.fit();
    }
    showSvg();
  } catch (e) {
    showEmpty();
    showNotif(`Erreur JS renderer: ${e.message}`, 'error', 6000);
    console.error(e);
  }
}

/* ═══ UI states ═══════════════════════════════════════════════════════════ */
function showEmpty() {
  emptyState.classList.remove('hidden');
  spinner.classList.add('hidden');
  svgEl.classList.add('hidden');
  controls.classList.add('hidden');
}

function showSpinner() {
  emptyState.classList.add('hidden');
  spinner.classList.remove('hidden');
  // keep SVG hidden during brief calculation
}

function showSvg() {
  emptyState.classList.add('hidden');
  spinner.classList.add('hidden');
  svgEl.classList.remove('hidden');
  controls.classList.remove('hidden');
}

/* ═══ Textarea ════════════════════════════════════════════════════════════ */
textarea.addEventListener('input', () => {
  const len = textarea.value.length;
  charCount.textContent = `${len.toLocaleString('fr-FR')} caractère${len !== 1 ? 's' : ''}`;
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => renderMindmap(), DEBOUNCE_MS);
});

/* ═══ Open file — via API Python (PowerShell COM, thread-safe) ═══════════ */
async function openFileViaPython() {
  try {
    showNotif('Ouverture du fichier…', 'info', 1500);
    const content = await window.pywebview.api.open_file_dialog();
    if (content === null || content === undefined) {
      // User cancelled — silent
      hideNotif();
      return;
    }
    if (content === '__ERROR__') {
      showNotif('Impossible de lire le fichier.', 'error');
      return;
    }
    textarea.value = content;
    textarea.dispatchEvent(new Event('input'));
    showNotif('Fichier chargé avec succès.', 'success');
  } catch (e) {
    showNotif(`Erreur ouverture : ${e.message}`, 'error');
    console.error('openFileViaPython error:', e);
  }
}

document.getElementById('btn-open').addEventListener('click', openFileViaPython);

/* ═══ Refresh & Fit buttons ═══════════════════════════════════════════════ */
document.getElementById('btn-refresh').addEventListener('click', () => {
  clearTimeout(debounceTimer);
  renderMindmap();
});
document.getElementById('btn-fit').addEventListener('click', () => {
  if (mm) mm.fit();
});

/* ═══ Clear ═══════════════════════════════════════════════════════════════ */
document.getElementById('btn-clear').addEventListener('click', () => {
  textarea.value = '';
  textarea.dispatchEvent(new Event('input'));
  showEmpty();
  if (mm) { mm.destroy(); mm = null; }
});

/* ═══ Helper: save via Python tkinter save dialog ═════════════════════════ */
async function saveViaDialog(content, extension) {
  try {
    const result = await window.pywebview.api.save_file_dialog(content, extension);
    if (result === true) showNotif(`Fichier .${extension} sauvegardé avec succès ! ✓`, 'success');
    else if (result === false) showNotif('Sauvegarde annulée.', 'info', 2000);
    else showNotif(`Erreur : ${result}`, 'error');
  } catch (e) {
    showNotif(`Erreur lors de la sauvegarde : ${e.message}`, 'error');
  }
}

/* ═══ Export SVG ══════════════════════════════════════════════════════════ */
document.getElementById('btn-export-svg').addEventListener('click', async () => {
  if (!mm || textarea.value.trim() === '') {
    showNotif("Aucune Mind Map à exporter.", 'info'); return;
  }
  try {
    const clone = svgEl.cloneNode(true);
    clone.classList.remove('hidden');
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    const bbox = svgEl.getBoundingClientRect();
    if (bbox.width) clone.setAttribute('width', bbox.width);
    if (bbox.height) clone.setAttribute('height', bbox.height);

    // Add essential font styling
    const styleEl = document.createElementNS('http://www.w3.org/2000/svg', 'style');
    styleEl.textContent = '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap"); text { font-family: Inter, sans-serif; font-size: 14px; }';
    clone.prepend(styleEl);

    // Reset transform on Markmap generic wrapper if present so it exports centered
    const g = clone.querySelector('g');
    if (g && mm.state?.transform) {
      g.setAttribute('transform', 'translate(50, 50) scale(1)');
    }

    await saveViaDialog('<?xml version="1.0" encoding="UTF-8"?>\n' + clone.outerHTML, 'svg');
  } catch (e) {
    showNotif(`Erreur export SVG : ${e.message}`, 'error');
  }
});

/* ═══ Export HTML ═════════════════════════════════════════════════════════ */
document.getElementById('btn-export-html').addEventListener('click', async () => {
  if (!mm || textarea.value.trim() === '') {
    showNotif("Aucune Mind Map à exporter.", 'info'); return;
  }

  showNotif('Préparation de l\'export…', 'info', 0);

  try {
    // Load vendor scripts from Python (reads local files — no CDN dependency)
    const vendors = await window.pywebview.api.get_vendor_scripts();
    if (!vendors) {
      showNotif('Erreur : impossible de lire les scripts vendor.', 'error');
      return;
    }

    const md = textarea.value;
    const safeMd = md.replace(/\\/g, '\\\\').replace(/`/g, '\\`').replace(/\$/g, '\\$');

    // Fully standalone HTML — all scripts embedded inline, zero network dependency
    const standaloneHtml = `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Mind Map Export</title>
  <style>
    html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #fff; }
    svg { width: 100%; height: 100%; display: block; }
  </style>
  <script>${vendors.d3}</script>
  <script>${vendors.markmap_lib}</script>
  <script>${vendors.markmap_view}</script>
</head>
<body>
  <svg id="markmap"></svg>
  <script>
    const md = \`${safeMd}\`;
    const { Transformer, Markmap } = window.markmap;
    const transformer = new Transformer();
    const { root } = transformer.transform(md);
    Markmap.create(document.getElementById('markmap'), { autoFit: true }, root);
  </script>
</body>
</html>`;

    await saveViaDialog(standaloneHtml, 'html');
  } catch (e) {
    showNotif(`Erreur export HTML : ${e.message}`, 'error');
    console.error(e);
  }
});

/* ═══ Resizer ═════════════════════════════════════════════════════════════ */
(function () {
  const resizer = document.getElementById('resizer');
  const panelLeft = document.getElementById('panel-input');
  const main = document.getElementById('main');
  let isDragging = false, startX = 0, startW = 0;

  resizer.addEventListener('mousedown', (e) => {
    isDragging = true; startX = e.clientX;
    startW = panelLeft.getBoundingClientRect().width;
    resizer.classList.add('active');
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
  });
  document.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const total = main.getBoundingClientRect().width;
    const newW = Math.min(Math.max(startW + (e.clientX - startX), 200), total - 200);
    panelLeft.style.width = `${newW}px`;
    panelLeft.style.flex = 'none';
  });
  document.addEventListener('mouseup', () => {
    if (!isDragging) return;
    isDragging = false;
    resizer.classList.remove('active');
    document.body.style.cursor = '';
    document.body.style.userSelect = '';
    if (mm) setTimeout(() => mm.fit(), 50); // fit after resize
  });
})();

/* ═══ Keyboard shortcuts ══════════════════════════════════════════════════ */
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'o') {
    e.preventDefault();
    openFileViaPython();
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    clearTimeout(debounceTimer);
    renderMindmap();
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
    e.preventDefault();
    if (mm) mm.fit();
  }
});

/* ═══ Bootstrap ═══════════════════════════════════════════════════════════ */
window.addEventListener('pywebviewready', async () => {
  // Load sample to start
  try {
    const sample = await window.pywebview.api.get_sample();
    if (sample) {
      textarea.value = sample;
      textarea.dispatchEvent(new Event('input'));
    }
  } catch (e) { console.error('Erreur API pywebview init', e); }
});

// Fallback if pywebviewready already fired
if (window.pywebview) {
  window.dispatchEvent(new Event('pywebviewready'));
}
