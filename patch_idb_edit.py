#!/usr/bin/env python3
"""
Patch wardrobe.html with three changes:
  1. Migrate photos from localStorage to IndexedDB
  2. Add Edit Item modal
  3. iPhone / iOS fixes
"""

import sys

PATH = '/sessions/stoic-admiring-brahmagupta/mnt/outputs/wardrobe.html'

with open(PATH, 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)
errors = []

# ============================================================
# CHANGE 1a — Replace the entire photo functions block
# ============================================================

OLD_PHOTOS_BLOCK = """// Photos
function getPhotos(id) {
  try {
    const arr = JSON.parse(localStorage.getItem('photos_'+id));
    if (Array.isArray(arr) && arr.length) return arr;
  } catch(e){}
  const single = localStorage.getItem('photo_'+id);
  if (single) {
    const arr = [single];
    localStorage.setItem('photos_'+id, JSON.stringify(arr));
    return arr;
  }
  return [];
}
function getPrimary(id) { return getPhotos(id)[0] || null; }
function addPhoto(id, dataUrl) {
  const arr = getPhotos(id);
  arr.push(dataUrl);
  try { localStorage.setItem('photos_'+id, JSON.stringify(arr)); }
  catch(e) { arr.pop(); throw e; }
}
function removePhoto(id, idx) {
  const arr = getPhotos(id);
  arr.splice(idx, 1);
  localStorage.setItem('photos_'+id, JSON.stringify(arr));
}"""

NEW_PHOTOS_BLOCK = """// ── IndexedDB Photo Storage ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
let photoDB = null;
let photoCache = {};  // itemId -> base64[] (in-memory, loaded at startup)

function openPhotoDB() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('wardrobe_photos_v1', 1);
    req.onupgradeneeded = e => e.target.result.createObjectStore('photos', { keyPath: 'id' });
    req.onsuccess = e => { photoDB = e.target.result; resolve(photoDB); };
    req.onerror = () => reject(req.error);
  });
}

function savePhotosIDB(id, arr) {
  if (!photoDB) return Promise.resolve();
  return new Promise(resolve => {
    const tx = photoDB.transaction('photos', 'readwrite');
    const store = tx.objectStore('photos');
    if (arr.length === 0) store.delete(id); else store.put({ id, photos: arr });
    tx.oncomplete = resolve;
    tx.onerror = resolve;
  });
}

async function initPhotos() {
  try {
    await openPhotoDB();
    // Load all photos from IndexedDB into cache
    await new Promise(resolve => {
      const tx = photoDB.transaction('photos', 'readonly');
      const req = tx.objectStore('photos').getAll();
      req.onsuccess = e => { e.target.result.forEach(r => { photoCache[r.id] = r.photos || []; }); resolve(); };
      req.onerror = resolve;
    });
    // Migrate any photos still in localStorage (one-time)
    const lsKeys = Object.keys(localStorage).filter(k => k.startsWith('photos_') || k.startsWith('photo_'));
    for (const key of lsKeys) {
      try {
        const id = key.replace(/^photos?_/, '');
        const raw = localStorage.getItem(key);
        const arr = key.startsWith('photos_') ? JSON.parse(raw) : [raw];
        if (Array.isArray(arr) && arr.length) {
          photoCache[id] = [...(photoCache[id] || []), ...arr];
          await savePhotosIDB(id, photoCache[id]);
          localStorage.removeItem(key);
        }
      } catch(e) {}
    }
  } catch(e) {
    console.warn('IndexedDB not available, falling back to localStorage', e);
  }
}

// Photo API (sync reads from cache, async writes to IDB)
function getPhotos(id) { return photoCache[id] || []; }
function getPrimary(id) { return getPhotos(id)[0] || null; }

function addPhoto(id, dataUrl) {
  const arr = [...getPhotos(id), dataUrl];
  photoCache[id] = arr;
  savePhotosIDB(id, arr).catch(() => toast('Photo save error'));
}

function removePhoto(id, idx) {
  const arr = [...getPhotos(id)];
  arr.splice(idx, 1);
  photoCache[id] = arr;
  savePhotosIDB(id, arr);
}"""

if OLD_PHOTOS_BLOCK in html:
    html = html.replace(OLD_PHOTOS_BLOCK, NEW_PHOTOS_BLOCK, 1)
    print('[OK] Change 1a: Replaced photo functions block with IndexedDB version')
else:
    errors.append('Change 1a FAILED: could not find photo functions block')
    print('[FAIL] Change 1a: photo functions block not found')

# ============================================================
# CHANGE 1b — Update INIT block to call initPhotos
# ============================================================

OLD_INIT = """load();
fetchWeather();
seedData();
renderWardrobe();"""

NEW_INIT = """async function init() {
  await initPhotos();
  load();
  fetchWeather();
  seedData();
  renderWardrobe();
}
init();"""

if OLD_INIT in html:
    html = html.replace(OLD_INIT, NEW_INIT, 1)
    print('[OK] Change 1b: Updated INIT block to use async init() with initPhotos()')
else:
    errors.append('Change 1b FAILED: could not find INIT block')
    print('[FAIL] Change 1b: INIT block not found')

# ============================================================
# CHANGE 1c — Update deletePhoto to use removePhoto properly
# ============================================================

OLD_DELETE_PHOTO = """function deletePhoto(id, idx) {
  removePhoto(id, idx);
  if (detailPhotoIdx >= getPhotos(id).length) detailPhotoIdx = Math.max(0, getPhotos(id).length-1);
  renderDetail(id); toast('Photo removed');
}"""

NEW_DELETE_PHOTO = """function deletePhoto(id, idx) {
  removePhoto(id, idx);
  const remaining = getPhotos(id).length;
  detailPhotoIdx = Math.max(0, Math.min(detailPhotoIdx, remaining - 1));
  renderDetail(id);
}"""

if OLD_DELETE_PHOTO in html:
    html = html.replace(OLD_DELETE_PHOTO, NEW_DELETE_PHOTO, 1)
    print('[OK] Change 1c: Updated deletePhoto body')
else:
    errors.append('Change 1c FAILED: could not find deletePhoto function body')
    print('[FAIL] Change 1c: deletePhoto function body not found')

# ============================================================
# CHANGE 1d — Update importData to use photoCache/savePhotosIDB
# ============================================================

OLD_IMPORT_PHOTOS = """        if (data.photos) Object.entries(data.photos).forEach(([id, photos]) => {
          localStorage.setItem('photos_'+id, JSON.stringify(photos));
        });"""

NEW_IMPORT_PHOTOS = """        if (data.photos) Object.entries(data.photos).forEach(([id, photos]) => {
          photoCache[id] = photos;
          savePhotosIDB(id, photos);
        });"""

if OLD_IMPORT_PHOTOS in html:
    html = html.replace(OLD_IMPORT_PHOTOS, NEW_IMPORT_PHOTOS, 1)
    print('[OK] Change 1d: Updated importData to use photoCache/savePhotosIDB')
else:
    errors.append('Change 1d FAILED: could not find importData photos block')
    print('[FAIL] Change 1d: importData photos block not found')

# ============================================================
# CHANGE 1e — Update deleteItem to also clean up IndexedDB photos
# ============================================================

OLD_DELETE_ITEM = """  S.items = S.items.filter(i=>i.id!==id);
  S.outfits.forEach(o => { o.itemIds = o.itemIds.filter(x=>x!==id); });
  save(); showView('wardrobe'); toast('Item deleted');"""

NEW_DELETE_ITEM = """  S.items = S.items.filter(i=>i.id!==id);
  S.outfits.forEach(o => { o.itemIds = o.itemIds.filter(x=>x!==id); });
  // Clean up photos from IndexedDB
  delete photoCache[id];
  if (photoDB) {
    const tx = photoDB.transaction('photos','readwrite');
    tx.objectStore('photos').delete(id);
  }
  save(); showView('wardrobe'); toast('Item deleted');"""

if OLD_DELETE_ITEM in html:
    html = html.replace(OLD_DELETE_ITEM, NEW_DELETE_ITEM, 1)
    print('[OK] Change 1e: Updated deleteItem to clean up IndexedDB photos')
else:
    errors.append('Change 1e FAILED: could not find deleteItem body')
    print('[FAIL] Change 1e: deleteItem body not found')

# ============================================================
# CHANGE 2a — Add Edit modal CSS before </style>
# ============================================================

EDIT_CSS = """/* ── EDIT MODAL ── */
.edit-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:300;display:flex;align-items:flex-end;justify-content:center}
.edit-modal-sheet{background:var(--cream);border-radius:18px 18px 0 0;width:100%;max-width:520px;max-height:90vh;overflow-y:auto;padding:20px 18px 36px}
.edit-field-label{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:var(--navy);font-weight:600;margin:14px 0 5px}
.edit-input{width:100%;padding:10px 12px;border:1.5px solid #ccc;border-radius:8px;font-size:16px;background:#fff;font-family:inherit}
.edit-input:focus{outline:none;border-color:var(--navy)}
.edit-select{width:100%;padding:10px 12px;border:1.5px solid #ccc;border-radius:8px;font-size:16px;background:#fff;font-family:inherit;appearance:none}
.edit-color-grid{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
.edit-color-swatch{width:30px;height:30px;border-radius:50%;cursor:pointer;border:3px solid transparent;transition:border-color .15s}
.edit-color-swatch.selected{border-color:var(--navy)}
.edit-occ-grid{display:flex;flex-wrap:wrap;gap:6px}
.edit-chip{padding:6px 13px;border-radius:16px;border:1.5px solid var(--navy);background:transparent;color:var(--navy);font-size:.8rem;cursor:pointer}
.edit-chip.active{background:var(--navy);color:var(--cream)}
.edit-save-btn{width:100%;padding:13px;background:var(--navy);color:var(--cream);border:none;border-radius:10px;font-size:1rem;font-weight:600;cursor:pointer;margin-top:18px}
.edit-cancel-btn{width:100%;padding:10px;background:transparent;border:none;color:#888;font-size:.85rem;cursor:pointer;margin-top:6px}
@media(max-width:480px){
  .detail-actions{flex-direction:column}
  .detail-actions .btn{width:100%;justify-content:center}
}
</style>"""

OLD_STYLE_CLOSE = """</style>"""

if OLD_STYLE_CLOSE in html:
    html = html.replace(OLD_STYLE_CLOSE, EDIT_CSS, 1)
    print('[OK] Change 2a+3b: Added Edit modal CSS and mobile media query before </style>')
else:
    errors.append('Change 2a FAILED: could not find </style>')
    print('[FAIL] Change 2a: </style> not found')

# ============================================================
# CHANGE 2b — Add Edit modal JS functions before </script>
# ============================================================

EDIT_JS = """// ============================================================
// EDIT ITEM MODAL
// ============================================================
let editItemColor = null;

function openEditModal(id) {
  const item = getItem(id);
  if (!item) return;
  editItemColor = { hex: item.color, name: item.colorName };

  const colorSwatches = COLORS.map(c =>
    `<div class="edit-color-swatch ${c.hex===item.color?'selected':''}"
      style="background:${c.hex}" title="${c.name}"
      onclick="selectEditColor('${c.hex}','${c.name}')"></div>`
  ).join('');

  const occChips = OCCASIONS.map(o =>
    `<button class="edit-chip ${(item.occasions||[]).includes(o)?'active':''}"
      onclick="this.classList.toggle('active')" data-occ="${o}">${o}</button>`
  ).join('');

  const seaOptions = SEASONS.map(s =>
    `<option value="${s}" ${item.season===s?'selected':''}>${s}</option>`
  ).join('');

  const catOptions = CATS.map(c =>
    `<option value="${c}" ${item.category===c?'selected':''}>${c}</option>`
  ).join('');

  const overlay = document.createElement('div');
  overlay.className = 'edit-modal-overlay';
  overlay.id = 'edit-modal-overlay';
  overlay.onclick = e => { if (e.target === overlay) closeEditModal(); };
  overlay.innerHTML = `<div class="edit-modal-sheet">
    <div style="width:40px;height:4px;background:#ccc;border-radius:2px;margin:0 auto 16px"></div>
    <div style="font-family:Georgia,serif;font-size:1.2rem;color:var(--navy);margin-bottom:4px;text-align:center">Edit Item</div>

    <div class="edit-field-label">Name</div>
    <input id="edit-name" class="edit-input" type="text" value="${item.name.replace(/"/g,'&quot;')}" placeholder="Item name">

    <div class="edit-field-label">Category</div>
    <select id="edit-cat" class="edit-select">${catOptions}</select>

    <div class="edit-field-label">Color</div>
    <div class="edit-color-grid" id="edit-color-grid">${colorSwatches}</div>

    <div class="edit-field-label">Occasions</div>
    <div class="edit-occ-grid" id="edit-occ-chips">${occChips}</div>

    <div class="edit-field-label">Season</div>
    <select id="edit-season" class="edit-select"><option value="year-round">Year-round</option>${seaOptions}</select>

    <div class="edit-field-label">Purchase Price ($)</div>
    <input id="edit-price" class="edit-input" type="number" min="0" step="1" value="${item.price||0}" placeholder="0">

    <button class="edit-save-btn" onclick="saveItemEdit('${id}')">Save Changes</button>
    <button class="edit-cancel-btn" onclick="closeEditModal()">Cancel</button>
  </div>`;
  document.body.appendChild(overlay);
}

function selectEditColor(hex, name) {
  editItemColor = { hex, name };
  document.querySelectorAll('.edit-color-swatch').forEach(s => {
    s.classList.toggle('selected', s.style.background === hex || s.style.backgroundColor === hex);
  });
}

function saveItemEdit(id) {
  const item = getItem(id);
  if (!item) return;
  const name = document.getElementById('edit-name').value.trim();
  if (!name) { toast('Name is required'); return; }
  item.name = name;
  item.category = document.getElementById('edit-cat').value;
  item.color = editItemColor.hex;
  item.colorName = editItemColor.name;
  item.season = document.getElementById('edit-season').value;
  item.price = parseFloat(document.getElementById('edit-price').value) || 0;
  item.occasions = Array.from(document.querySelectorAll('#edit-occ-chips .edit-chip.active'))
    .map(el => el.dataset.occ);
  save();
  closeEditModal();
  renderDetail(id);
  toast('Item updated!');
}

function closeEditModal() {
  const el = document.getElementById('edit-modal-overlay');
  if (el) el.remove();
}

</script>"""

OLD_SCRIPT_CLOSE = """</script>"""

if OLD_SCRIPT_CLOSE in html:
    html = html.replace(OLD_SCRIPT_CLOSE, EDIT_JS, 1)
    print('[OK] Change 2b: Added Edit modal JS functions before </script>')
else:
    errors.append('Change 2b FAILED: could not find </script>')
    print('[FAIL] Change 2b: </script> not found')

# ============================================================
# CHANGE 2c — Add Edit button to renderDetail
# ============================================================

OLD_DETAIL_BTNS = """<button class="btn btn-primary" onclick="showView('builder');addToBuilder('${id}')">&#9733; Build Outfit</button>
          <button class="btn btn-danger" onclick="deleteItem('${id}')">&#x2715; Delete</button>"""

NEW_DETAIL_BTNS = """<button class="btn btn-primary" onclick="showView('builder');addToBuilder('${id}')">&#9733; Build Outfit</button>
          <button class="btn btn-secondary" onclick="openEditModal('${id}')">&#9998; Edit</button>
          <button class="btn btn-danger" onclick="deleteItem('${id}')">&#x2715; Delete</button>"""

if OLD_DETAIL_BTNS in html:
    html = html.replace(OLD_DETAIL_BTNS, NEW_DETAIL_BTNS, 1)
    print('[OK] Change 2c: Added Edit button to renderDetail action bar')
else:
    errors.append('Change 2c FAILED: could not find detail action buttons')
    print('[FAIL] Change 2c: detail action buttons not found')

# ============================================================
# CHANGE 3a — Add font-size:16px to inputs/selects/textareas
# ============================================================

OLD_INPUT_RULE = """input,select,textarea{font-family:inherit}"""
NEW_INPUT_RULE = """input,select,textarea{font-family:inherit;font-size:16px!important}"""

if OLD_INPUT_RULE in html:
    html = html.replace(OLD_INPUT_RULE, NEW_INPUT_RULE, 1)
    print('[OK] Change 3a: Added font-size:16px to input/select/textarea rule')
else:
    errors.append('Change 3a FAILED: could not find input/select/textarea font-family rule')
    print('[FAIL] Change 3a: input/select/textarea font-family rule not found')

# ============================================================
# Write the patched file
# ============================================================

with open(PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print()
print(f'Original size: {original_len:,} chars')
print(f'Patched size:  {len(html):,} chars')
print(f'Delta:         +{len(html)-original_len:,} chars')
print()

# ============================================================
# VERIFICATION CHECKLIST
# ============================================================

checks = [
    ('photoCache defined',            'let photoCache = {};' in html),
    ('openPhotoDB function present',  'function openPhotoDB()' in html),
    ('initPhotos function present',   'async function initPhotos()' in html),
    ('savePhotosIDB function present','function savePhotosIDB(' in html),
    ('async function init() present', 'async function init()' in html),
    ('openEditModal function present','function openEditModal(' in html),
    ('saveItemEdit function present', 'function saveItemEdit(' in html),
    ('Edit button in renderDetail',   'openEditModal' in html and 'Edit</button>' in html),
    ('edit-modal CSS present',        '.edit-modal-overlay' in html),
    ('font-size:16px on inputs',      'font-size:16px!important' in html),
    ('File size > 245000 chars',      len(html) > 245000),
]

print('VERIFICATION CHECKLIST')
print('=' * 50)
all_ok = True
for label, result in checks:
    status = 'PASS' if result else 'FAIL'
    if not result:
        all_ok = False
    print(f'  [{status}] {label}')

print()
if errors:
    print('PATCH ERRORS:')
    for e in errors:
        print(f'  - {e}')
else:
    print('All patches applied without errors.')

if all_ok and not errors:
    print('SUCCESS: All changes applied and verified.')
else:
    print('WARNING: Some checks failed. Review output above.')
    sys.exit(1)
