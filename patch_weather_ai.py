import re

with open('/sessions/stoic-admiring-brahmagupta/mnt/outputs/wardrobe.html', 'r') as f:
    html = f.read()

# ─────────────────────────────────────────────────────────────
# 1. ADD CSS  (insert before </style>)
# ─────────────────────────────────────────────────────────────
NEW_CSS = """
/* ── WEATHER WIDGET ── */
.weather-bar{display:flex;align-items:center;gap:10px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.15);border-radius:10px;padding:10px 16px;margin:0 0 14px 0;font-size:.85rem;color:var(--cream);cursor:pointer;transition:background .2s}
.weather-bar:hover{background:rgba(255,255,255,.13)}
.weather-icon{font-size:1.5rem;line-height:1}
.weather-temp{font-size:1.15rem;font-weight:700;color:var(--khaki)}
.weather-desc{flex:1;color:rgba(255,255,255,.8)}
.weather-advice{font-size:.75rem;color:rgba(255,255,255,.6);margin-left:auto;text-align:right;max-width:160px;line-height:1.3}
.weather-loading{color:rgba(255,255,255,.5);font-style:italic}

/* ── SUGGESTION MODAL ── */
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:200;display:flex;align-items:flex-end;justify-content:center}
.modal-sheet{background:var(--cream);border-radius:18px 18px 0 0;width:100%;max-width:520px;max-height:88vh;overflow-y:auto;padding:24px 20px 32px}
.modal-handle{width:40px;height:4px;background:#ccc;border-radius:2px;margin:0 auto 18px}
.modal-title{font-family:Georgia,serif;font-size:1.2rem;color:var(--navy);margin-bottom:16px;text-align:center}
.occ-chips{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:18px;justify-content:center}
.occ-chip{padding:7px 16px;border-radius:20px;border:1.5px solid var(--navy);background:transparent;color:var(--navy);font-size:.8rem;cursor:pointer;transition:all .2s}
.occ-chip.active{background:var(--navy);color:var(--cream)}
.suggest-result{background:#fff;border:1px solid #ddd;border-radius:12px;padding:16px;margin-top:8px}
.suggest-result-title{font-weight:600;color:var(--navy);margin-bottom:10px;font-size:.95rem}
.suggest-item-row{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid #f0f0f0}
.suggest-item-row:last-child{border-bottom:none}
.suggest-item-thumb{width:40px;height:40px;border-radius:6px;object-fit:cover;background:#eee}
.suggest-item-info{flex:1}
.suggest-item-name{font-size:.85rem;color:#333;font-weight:500}
.suggest-item-cat{font-size:.73rem;color:#888;text-transform:capitalize}
.suggest-actions{display:flex;gap:10px;margin-top:14px}
.btn-suggest-save{flex:1;padding:11px;background:var(--navy);color:var(--cream);border:none;border-radius:8px;font-size:.85rem;cursor:pointer}
.btn-suggest-again{flex:1;padding:11px;background:transparent;color:var(--navy);border:1.5px solid var(--navy);border-radius:8px;font-size:.85rem;cursor:pointer}
.btn-ask-claude{width:100%;padding:11px;background:linear-gradient(135deg,#6c47d4,#a06ee0);color:#fff;border:none;border-radius:8px;font-size:.85rem;cursor:pointer;margin-top:8px;display:flex;align-items:center;justify-content:center;gap:6px}
.btn-ask-claude:disabled{opacity:.5;cursor:default}
.claude-response{background:#f8f4ff;border:1px solid #d0b0f0;border-radius:10px;padding:14px;margin-top:10px;font-size:.84rem;color:#333;line-height:1.55;white-space:pre-wrap}
.no-suggestion{text-align:center;color:#888;padding:20px;font-size:.9rem}

/* ── SETTINGS VIEW ── */
.settings-wrap{padding:16px 0 40px}
.settings-section{background:#fff;border:1px solid #e0d8cc;border-radius:12px;padding:18px;margin-bottom:16px}
.settings-section h3{font-family:Georgia,serif;font-size:1rem;color:var(--navy);margin:0 0 12px}
.settings-row{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f0ebe0}
.settings-row:last-child{border-bottom:none}
.settings-label{font-size:.85rem;color:#444}
.settings-hint{font-size:.75rem;color:#888;margin-top:2px}
.settings-input{width:100%;padding:10px 12px;border:1.5px solid #ccc;border-radius:8px;font-size:.85rem;margin-top:8px;font-family:monospace}
.settings-input:focus{outline:none;border-color:var(--navy)}
.btn-settings-save{width:100%;padding:11px;background:var(--navy);color:var(--cream);border:none;border-radius:8px;font-size:.85rem;cursor:pointer;margin-top:10px}
.settings-key-status{font-size:.78rem;margin-top:6px;padding:6px 10px;border-radius:6px}
.key-ok{background:#eafaea;color:#1d6b1d;border:1px solid #b4d9b4}
.key-none{background:#f8f4ec;color:#7a5a00;border:1px solid #e0cc80}

/* ── SUGGEST BUTTON IN OUTFITS ── */
.btn-suggest-outfit{display:flex;align-items:center;gap:6px;padding:9px 16px;background:var(--forest);color:var(--cream);border:none;border-radius:8px;font-size:.82rem;cursor:pointer;transition:opacity .2s}
.btn-suggest-outfit:hover{opacity:.85}
"""

html = html.replace('</style>', NEW_CSS + '\n</style>', 1)
print("✓ CSS added")

# ─────────────────────────────────────────────────────────────
# 2. ADD SETTINGS NAV TAB (after the last nav-tab "add")
# ─────────────────────────────────────────────────────────────
ADD_TAB_END = '''      <span class="tab-label">Add</span>
    </button>
  </div>
</nav>'''

SETTINGS_TAB = '''      <span class="tab-label">Add</span>
    </button>
    <button class="nav-tab" data-view="settings">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
      <span class="tab-label">Settings</span>
    </button>
  </div>
</nav>'''

html = html.replace(ADD_TAB_END, SETTINGS_TAB, 1)
print("✓ Settings nav tab added")

# ─────────────────────────────────────────────────────────────
# 3. ADD VIEW DIV FOR SETTINGS
# ─────────────────────────────────────────────────────────────
html = html.replace(
    '<div id="view-outfit-detail" class="view"></div>',
    '<div id="view-outfit-detail" class="view"></div>\n<div id="view-settings" class="view"></div>\n<div id="modal-suggest" style="display:none" class="modal-overlay"></div>',
    1
)
print("✓ Settings view div added")

# ─────────────────────────────────────────────────────────────
# 4. ADD STATE VARIABLES (after addFormPrefill line)
# ─────────────────────────────────────────────────────────────
html = html.replace(
    'let addFormPrefill = null;',
    '''let addFormPrefill = null;
let weatherData = null;          // { temp, code, desc, icon, advice, lat, lon }
let suggestOccasion = 'casual';  // last used occasion in suggest modal
let suggestResult = null;        // last suggested outfit items array
let claudeLoading = false;       // AI request in-flight''',
    1
)
print("✓ State variables added")

# ─────────────────────────────────────────────────────────────
# 5. ADD ALL NEW FUNCTIONS (before </script>)
# ─────────────────────────────────────────────────────────────
NEW_FUNCTIONS = """
// ============================================================
// WEATHER
// ============================================================
const WMO_MAP = {
  0:{icon:'☀️',desc:'Clear'},1:{icon:'🌤',desc:'Mostly Clear'},2:{icon:'⛅',desc:'Partly Cloudy'},
  3:{icon:'☁️',desc:'Overcast'},45:{icon:'🌫',desc:'Foggy'},48:{icon:'🌫',desc:'Icy Fog'},
  51:{icon:'🌦',desc:'Light Drizzle'},53:{icon:'🌧',desc:'Drizzle'},55:{icon:'🌧',desc:'Heavy Drizzle'},
  61:{icon:'🌧',desc:'Light Rain'},63:{icon:'🌧',desc:'Rain'},65:{icon:'🌧',desc:'Heavy Rain'},
  71:{icon:'🌨',desc:'Light Snow'},73:{icon:'❄️',desc:'Snow'},75:{icon:'❄️',desc:'Heavy Snow'},
  80:{icon:'🌦',desc:'Rain Showers'},81:{icon:'🌧',desc:'Heavy Showers'},82:{icon:'⛈',desc:'Violent Showers'},
  95:{icon:'⛈',desc:'Thunderstorm'},96:{icon:'⛈',desc:'Hail Storm'},99:{icon:'⛈',desc:'Severe Thunderstorm'}
};

function fetchWeather() {
  if (!navigator.geolocation) return;
  navigator.geolocation.getCurrentPosition(pos => {
    const {latitude: lat, longitude: lon} = pos.coords;
    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current=temperature_2m,weathercode,windspeed_10m&temperature_unit=fahrenheit&windspeed_unit=mph&timezone=auto`)
      .then(r => r.json())
      .then(data => {
        const c = data.current;
        const code = c.weathercode;
        const wmo = WMO_MAP[code] || WMO_MAP[Math.floor(code/10)*10] || {icon:'🌡',desc:'Check outside'};
        const temp = Math.round(c.temperature_2m);
        const wind = Math.round(c.windspeed_10m);
        weatherData = { temp, code, wind, icon: wmo.icon, desc: wmo.desc, advice: weatherAdvice(temp, code, wind) };
        // refresh wardrobe view if active
        if (currentView === 'wardrobe') renderWardrobe();
      })
      .catch(() => {}); // silently fail – offline or blocked
  }, () => {}, { timeout: 8000 });
}

function weatherAdvice(temp, code, wind) {
  const parts = [];
  if (temp < 32) parts.push('Heavy coat & layers');
  else if (temp < 45) parts.push('Warm coat needed');
  else if (temp < 58) parts.push('Jacket or sweater');
  else if (temp < 70) parts.push('Light layer handy');
  else if (temp < 82) parts.push('Short sleeves fine');
  else parts.push('Dress light & cool');
  if ([51,53,55,61,63,65,80,81,82,95,96,99].includes(code)) parts.push('Rain gear advised');
  else if ([71,73,75].includes(code)) parts.push('Snow boots today');
  if (wind > 20) parts.push('Secure loose items');
  return parts.join(' · ');
}

function weatherClothingFilter(item) {
  // Returns true if item is appropriate given current weather
  if (!weatherData) return true;
  const t = weatherData.temp;
  const code = weatherData.code;
  const isRain = [51,53,55,61,63,65,80,81,82,95,96,99].includes(code);
  const isSnow = [71,73,75].includes(code);
  const cat = item.category || '';
  const season = item.season || 'year-round';
  // Season gating
  if (t > 68 && season === 'fall/winter') return false;
  if (t < 52 && season === 'spring/summer') return false;
  // Heavy coats only when cold
  if (['coats'].includes(cat) && t > 60) return false;
  // Swim trunks only when warm
  if (cat === 'swim trunks' && t < 72) return false;
  // Athletic shorts only when warm
  if (cat === 'athletic shorts' && t < 60) return false;
  return true;
}

function renderWeatherBar() {
  if (!weatherData) {
    return `<div class="weather-bar weather-loading" onclick="fetchWeather()">
      <span>📍 Tap to load local weather & clothing suggestions</span>
    </div>`;
  }
  const {icon, desc, temp, advice} = weatherData;
  const color = temp < 40 ? '#7ec8e3' : temp < 60 ? '#b0d4f1' : temp < 75 ? '#ffe066' : '#ff9a3c';
  return `<div class="weather-bar" onclick="openSuggestModal()" title="Tap for outfit suggestions">
    <span class="weather-icon">${icon}</span>
    <span class="weather-temp" style="color:${color}">${temp}°F</span>
    <span class="weather-desc">${desc}</span>
    <span class="weather-advice">${advice}</span>
    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" fill="none" stroke-width="2" opacity=".5"><path d="M9 18l6-6-6-6"/></svg>
  </div>`;
}

// ============================================================
// SMART OUTFIT SUGGESTION ENGINE
// ============================================================
const OUTFIT_LAYERS = {
  tops:      ['t-shirts','button downs','polos','sweaters','sweatshirts','hoodies'],
  outer:     ['coats','jackets','blazers','sport coats','vests'],
  bottoms:   ['dress pants','khakis','jeans','shorts','athletic shorts','swim trunks'],
  shoes:     ['dress shoes','loafers','boots','sneakers','boat shoes'],
  acc:       ['belts','ties','bowties','pocket squares','watches','hats','scarves','gloves','socks']
};
const OCC_WEIGHTS = {
  formal:      {tops:['button downs'],outer:['blazers','sport coats','suits'],bottoms:['dress pants','khakis'],shoes:['dress shoes','loafers']},
  work:        {tops:['button downs','polos'],outer:['blazers','sport coats'],bottoms:['dress pants','khakis'],shoes:['dress shoes','loafers','boots']},
  'date night':{tops:['button downs','polos','sweaters'],outer:['blazers','sport coats','jackets'],bottoms:['khakis','dress pants','jeans'],shoes:['dress shoes','loafers','boots']},
  casual:      {tops:['t-shirts','polos','button downs','sweaters','sweatshirts'],outer:['jackets','coats'],bottoms:['jeans','khakis','shorts'],shoes:['sneakers','boat shoes','loafers','boots']},
  weekend:     {tops:['t-shirts','polos','sweaters','sweatshirts','hoodies'],outer:['jackets','coats'],bottoms:['jeans','shorts','khakis'],shoes:['sneakers','boat shoes','boots']},
  athletic:    {tops:['t-shirts','sweatshirts','hoodies'],outer:[],bottoms:['athletic shorts','shorts'],shoes:['sneakers']}
};

function pickOne(arr) { return arr[Math.floor(Math.random() * arr.length)] || null; }

function suggestOutfit(occasion, forceNew) {
  const occ = occasion || 'casual';
  const weights = OCC_WEIGHTS[occ] || OCC_WEIGHTS['casual'];
  const clean = S.items.filter(i => isWearable(i) && (!i.archived || i.archived === 'active'));
  const weatherOk = item => weatherClothingFilter(item);
  const occOk = item => !item.occasions || item.occasions.length === 0 || item.occasions.includes(occ);

  function pool(catList) {
    return clean.filter(i => catList.includes(i.category) && weatherOk(i) && occOk(i));
  }

  const topPool    = pool(weights.tops || OUTFIT_LAYERS.tops);
  const outerPool  = pool(weights.outer || OUTFIT_LAYERS.outer);
  const bottomPool = pool(weights.bottoms || OUTFIT_LAYERS.bottoms);
  const shoePool   = pool(weights.shoes || OUTFIT_LAYERS.shoes);
  const accPool    = pool(OUTFIT_LAYERS.acc);

  // Pick items
  const top    = pickOne(topPool);
  const bottom = pickOne(bottomPool);
  const shoe   = pickOne(shoePool);

  if (!top && !bottom) return null; // not enough items

  let result = [top, bottom, shoe].filter(Boolean);

  // Add outer layer if cold or rainy
  if (weatherData && (weatherData.temp < 60 || [51,53,55,61,63,65,80,81,82].includes(weatherData.code))) {
    const outer = pickOne(outerPool);
    if (outer) result.push(outer);
  }

  // Add 1-2 accessories
  const belt   = pickOne(accPool.filter(i => i.category === 'belts'));
  const watch  = pickOne(accPool.filter(i => i.category === 'watches'));
  const socks  = pickOne(accPool.filter(i => i.category === 'socks'));
  if (belt)  result.push(belt);
  if (watch) result.push(watch);
  if (socks) result.push(socks);
  if (weatherData && weatherData.temp < 45) {
    const scarf = pickOne(accPool.filter(i => i.category === 'scarves'));
    const glove = pickOne(accPool.filter(i => i.category === 'gloves'));
    if (scarf) result.push(scarf);
    if (glove) result.push(glove);
  }

  // Deduplicate by id
  const seen = new Set();
  result = result.filter(i => { if (!i || seen.has(i.id)) return false; seen.add(i.id); return true; });

  return result.length >= 2 ? result : null;
}

// ============================================================
// SUGGEST MODAL UI
// ============================================================
function openSuggestModal() {
  suggestResult = suggestOutfit(suggestOccasion);
  renderSuggestModal();
  document.getElementById('modal-suggest').style.display = 'flex';
}

function closeSuggestModal() {
  document.getElementById('modal-suggest').style.display = 'none';
}

function renderSuggestModal() {
  const modal = document.getElementById('modal-suggest');
  const hasKey = !!(localStorage.getItem('claude_api_key') || '').trim();
  const weather = weatherData
    ? `<div style="text-align:center;font-size:.8rem;color:#888;margin-bottom:12px">${weatherData.icon} ${weatherData.temp}°F · ${weatherData.desc}</div>`
    : '';
  const occButtons = ['casual','work','formal','date night','weekend','athletic']
    .map(o => `<button class="occ-chip ${o===suggestOccasion?'active':''}" onclick="setSuggestOcc('${o}')">${o}</button>`).join('');

  let resultHtml = '';
  if (!suggestResult) {
    resultHtml = `<div class="no-suggestion">Not enough clean items in your wardrobe for this occasion. Add more items or check the laundry!</div>`;
  } else {
    const rows = suggestResult.map(item => {
      const photos = JSON.parse(localStorage.getItem('photos_'+item.id)||'[]');
      const thumb = photos[0] ? `<img class="suggest-item-thumb" src="${photos[0]}" alt="">` : `<div class="suggest-item-thumb" style="display:flex;align-items:center;justify-content:center;color:#aaa">👕</div>`;
      return `<div class="suggest-item-row">${thumb}<div class="suggest-item-info"><div class="suggest-item-name">${item.name}</div><div class="suggest-item-cat">${item.category}</div></div></div>`;
    }).join('');
    resultHtml = `<div class="suggest-result"><div class="suggest-result-title">✦ Suggested Outfit</div>${rows}</div>
      <div class="suggest-actions">
        <button class="btn-suggest-again" onclick="reshuffleSuggest()">↺ Different</button>
        <button class="btn-suggest-save" onclick="saveSuggestedOutfit()">Save Outfit</button>
      </div>`;
  }

  const claudeBtn = hasKey
    ? `<button class="btn-ask-claude" ${claudeLoading?'disabled':''} onclick="askClaudeOutfit()">✨ ${claudeLoading?'Asking Claude...':'Ask Claude for a Suggestion'}</button>`
    : `<button class="btn-ask-claude" style="background:#999" onclick="showView('settings')">🔑 Add Claude API Key in Settings to unlock AI suggestions</button>`;

  modal.innerHTML = `<div class="modal-sheet">
    <div class="modal-handle"></div>
    <div class="modal-title">Outfit Suggestion</div>
    ${weather}
    <div class="occ-chips">${occButtons}</div>
    ${resultHtml}
    <div id="claude-response-area"></div>
    ${claudeBtn}
    <button onclick="closeSuggestModal()" style="width:100%;padding:9px;background:transparent;border:none;color:#999;font-size:.85rem;cursor:pointer;margin-top:8px">Close</button>
  </div>`;
}

function setSuggestOcc(occ) {
  suggestOccasion = occ;
  suggestResult = suggestOutfit(occ);
  renderSuggestModal();
}

function reshuffleSuggest() {
  suggestResult = suggestOutfit(suggestOccasion, true);
  renderSuggestModal();
}

function saveSuggestedOutfit() {
  if (!suggestResult || !suggestResult.length) return;
  const name = prompt('Name this outfit:', 'Suggested Outfit');
  if (!name) return;
  const id = uid();
  S.outfits.push({ id, name, items: suggestResult.map(i=>i.id), occasion: suggestOccasion, favorite: false });
  save(); closeSuggestModal(); showView('outfits');
  toast('Outfit saved!');
}

// ============================================================
// CLAUDE API INTEGRATION
// ============================================================
async function askClaudeOutfit() {
  const key = (localStorage.getItem('claude_api_key') || '').trim();
  if (!key) { toast('Add your Claude API key in Settings first'); showView('settings'); return; }
  claudeLoading = true;
  renderSuggestModal();

  // Build wardrobe summary (clean items only, first 60)
  const cleanItems = S.items.filter(i => isWearable(i) && (!i.archived || i.archived === 'active')).slice(0, 60);
  const itemList = cleanItems.map(i => `${i.name} (${i.category}${i.color?', '+i.colorName:''}${i.occasions&&i.occasions.length?', for: '+i.occasions.join('/'):''})`).join('\\n');
  const weatherStr = weatherData ? `Current weather: ${weatherData.temp}°F, ${weatherData.desc}.` : '';
  const prompt = `You are a stylish personal wardrobe assistant with a New England preppy aesthetic.\\n${weatherStr}\\nOccasion: ${suggestOccasion}.\\n\\nHere are my clean clothes:\\n${itemList}\\n\\nSuggest a great outfit from these items. Be specific (use exact item names from the list), explain why the combination works, and add one short style tip. Keep it under 120 words.`;

  try {
    const resp = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': key,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerous-direct-browser-access': 'true'
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 250,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    const data = await resp.json();
    if (data.error) throw new Error(data.error.message);
    const text = data.content[0].text;
    claudeLoading = false;
    renderSuggestModal();
    const area = document.getElementById('claude-response-area');
    if (area) area.innerHTML = `<div class="claude-response">✨ <strong>Claude says:</strong>\\n${text}</div>`;
  } catch(err) {
    claudeLoading = false;
    renderSuggestModal();
    const area = document.getElementById('claude-response-area');
    if (area) area.innerHTML = `<div class="claude-response" style="color:#c00">Error: ${err.message || 'Could not reach Claude API. Check your key in Settings.'}</div>`;
  }
}

// ============================================================
// SETTINGS VIEW
// ============================================================
function renderSettings() {
  const key = localStorage.getItem('claude_api_key') || '';
  const keyStatus = key.trim()
    ? `<div class="settings-key-status key-ok">✓ API key saved — Claude AI suggestions are enabled</div>`
    : `<div class="settings-key-status key-none">No key saved — outfit suggestions will use smart rules only</div>`;

  document.getElementById('view-settings').innerHTML = `<div class="page-inner"><div class="settings-wrap">
    <div style="font-family:Georgia,serif;font-size:1.3rem;color:var(--navy);margin-bottom:18px">⚙ Settings</div>

    <div class="settings-section">
      <h3>🤖 Claude AI Integration</h3>
      <p style="font-size:.82rem;color:#666;line-height:1.5;margin-bottom:10px">Add your Anthropic API key to unlock natural language outfit suggestions powered by Claude. Your key is stored only in your browser's localStorage — never sent anywhere except Anthropic's API.</p>
      <a href="https://console.anthropic.com/settings/keys" target="_blank" style="font-size:.8rem;color:var(--navy)">Get a key at console.anthropic.com →</a>
      <input class="settings-input" id="claude-key-input" type="password" placeholder="sk-ant-api03-..." value="${key}" autocomplete="off" spellcheck="false">
      ${keyStatus}
      <button class="btn-settings-save" onclick="saveClaudeKey()">Save API Key</button>
      ${key ? '<button onclick="clearClaudeKey()" style="width:100%;padding:9px;background:transparent;border:none;color:#c00;font-size:.82rem;cursor:pointer;margin-top:4px">Remove key</button>' : ''}
    </div>

    <div class="settings-section">
      <h3>📍 Weather</h3>
      <div class="settings-row">
        <div><div class="settings-label">Location access</div><div class="settings-hint">Used only to fetch weather from Open-Meteo. Never stored or shared.</div></div>
      </div>
      <button class="btn-settings-save" style="margin-top:12px" onclick="fetchWeather();toast('Fetching weather...')">Refresh Weather Now</button>
    </div>

    <div class="settings-section">
      <h3>💾 Data</h3>
      <button class="btn-settings-save" onclick="exportData()" style="margin-bottom:8px">Export Backup (JSON)</button>
      <button class="btn-settings-save" style="background:transparent;color:var(--navy);border:1.5px solid var(--navy)" onclick="document.getElementById('import-file').click()">Import Backup (JSON)</button>
      <input type="file" id="import-file" accept=".json" style="display:none" onchange="importData(event)">
    </div>
  </div></div>`;
}

function saveClaudeKey() {
  const key = (document.getElementById('claude-key-input').value || '').trim();
  localStorage.setItem('claude_api_key', key);
  toast(key ? 'API key saved!' : 'Key cleared');
  renderSettings();
}

function clearClaudeKey() {
  localStorage.removeItem('claude_api_key');
  toast('API key removed');
  renderSettings();
}
"""

html = html.replace('</script>', NEW_FUNCTIONS + '\n</script>', 1)
print("✓ New functions added")

# ─────────────────────────────────────────────────────────────
# 6. HOOK renderSettings INTO showView
# ─────────────────────────────────────────────────────────────
html = html.replace(
    "if (name === 'add') renderAdd();",
    "if (name === 'add') renderAdd();\n  if (name === 'settings') renderSettings();",
    1
)
print("✓ renderSettings hooked into showView")

# ─────────────────────────────────────────────────────────────
# 7. ADD WEATHER BAR TO renderWardrobe (after stats section)
# ─────────────────────────────────────────────────────────────
# Find the start of the renderWardrobe function and the items list render
# Insert weather bar near the top of the rendered content

old_wardrobe_inner = "  const cats = CATEGORIES.filter(c => S.items.some(i=>i.category===c));"
new_wardrobe_inner = "  const cats = CATEGORIES.filter(c => S.items.some(i=>i.category===c));\n  const weatherBarHtml = renderWeatherBar();"

html = html.replace(old_wardrobe_inner, new_wardrobe_inner, 1)
print("✓ weatherBarHtml variable injected in renderWardrobe")

# Now find where the HTML is assembled in renderWardrobe and insert the weather bar
# Look for the stats section / page-inner div opening
old_wardrobe_start = 'let html = `<div class="page-inner">'
new_wardrobe_start = 'let html = `<div class="page-inner">${weatherBarHtml}'

count = html.count(old_wardrobe_start)
if count:
    html = html.replace(old_wardrobe_start, new_wardrobe_start, 1)
    print("✓ Weather bar injected into wardrobe HTML")
else:
    # Try alternate insertion point
    old2 = "let html = `<div class='page-inner'>"
    if html.count(old2):
        html = html.replace(old2, f"let html = `<div class='page-inner'>${{weatherBarHtml}}", 1)
        print("✓ Weather bar injected (alt)")
    else:
        print("⚠ Could not find renderWardrobe html start — searching...")
        idx = html.find('function renderWardrobe()')
        snippet = html[idx:idx+800]
        print(repr(snippet[:400]))

# ─────────────────────────────────────────────────────────────
# 8. ADD SUGGEST OUTFIT BUTTON TO renderOutfits
# ─────────────────────────────────────────────────────────────
old_outfits_header = "function renderOutfits() {"
idx = html.find(old_outfits_header)
if idx != -1:
    # Find the first innerHTML assignment in renderOutfits
    end = html.find('document.getElementById(\'view-outfits\').innerHTML', idx)
    if end != -1:
        # Find where the header section is built — look for Outfits title string
        snippet_start = end
        snippet_end = html.find('`;\n', snippet_start) + 3
        snippet = html[snippet_start:snippet_end]
        # Try to find random outfit button to insert suggest button next to it
        old_random_btn = "onclick=\"wearRandomOutfit()\""
        if old_random_btn in snippet:
            new_snippet = snippet.replace(
                old_random_btn,
                old_random_btn + '''</button>
        <button class="btn-suggest-outfit" onclick="openSuggestModal()">
          <svg viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" fill="none" stroke-width="2"><path d="M12 2a10 10 0 1010 10"/><path d="M22 2L12 12"/><path d="M17 2h5v5"/></svg>
          Suggest''',
                1
            )
            html = html[:snippet_start] + new_snippet + html[snippet_end:]
            print("✓ Suggest outfit button added to Outfits header")
        else:
            print("⚠ Could not find random outfit button in outfits section")
    else:
        print("⚠ Could not find view-outfits innerHTML")

# ─────────────────────────────────────────────────────────────
# 9. CALL fetchWeather() ON LOAD
# ─────────────────────────────────────────────────────────────
# Find the init/load call at the bottom
old_init = "load();\nshowView('wardrobe');"
new_init = "load();\nfetchWeather();\nshowView('wardrobe');"

if html.count(old_init):
    html = html.replace(old_init, new_init, 1)
    print("✓ fetchWeather() called on load")
else:
    old_init2 = "load();\n  showView('wardrobe');"
    if html.count(old_init2):
        html = html.replace(old_init2, "load();\n  fetchWeather();\n  showView('wardrobe');", 1)
        print("✓ fetchWeather() called on load (alt)")
    else:
        print("⚠ Could not find load() call — searching for it")
        for line in ["load();", "showView('wardrobe')"]:
            idxl = html.rfind(line)
            print(f"  '{line}' last found at index {idxl}")

# ─────────────────────────────────────────────────────────────
# WRITE FILE
# ─────────────────────────────────────────────────────────────
with open('/sessions/stoic-admiring-brahmagupta/mnt/outputs/wardrobe.html', 'w') as f:
    f.write(html)

print(f"\\nFile written: {len(html):,} chars")
