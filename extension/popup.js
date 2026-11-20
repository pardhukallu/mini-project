const $ = (id) => document.getElementById(id);
const SENSITIVE = new Set(['debugger','proxy','webRequest','webRequestBlocking','nativeMessaging','cookies','history','downloads','management','clipboardRead','clipboardWrite','camera','microphone','geolocation']);
function classify(ext) {
  const perms = [...(ext.permissions || []), ...(ext.hostPermissions || [])];
  const high = perms.filter(p => SENSITIVE.has(p) || p === '<all_urls>' || p === '*://*/*' || p === 'http://*/*' || p === 'https://*/*');
  const medium = perms.filter(p => ['tabs','activeTab','scripting','contentSettings','notifications','geolocation','camera','microphone'].includes(p));
  const level = high.length ? 'high' : medium.length ? 'medium' : 'low';
  return {name: ext.name, permissions: perms, risk_level: level, reason: high.length ? `Sensitive permissions: ${high.join(', ')}` : medium.length ? `Broad or user-data access: ${medium.join(', ')}` : 'No high-impact declared permissions detected'};
}
async function run() {
  $('scan').disabled = true; $('status').textContent = 'Reading local extension metadata…'; $('results').innerHTML = '';
  const base = $('api').value.trim().replace(/\/$/, '');
  if ($('token').value.trim()) {
    try { const parsed = new URL(base); const pattern = `${parsed.protocol}//${parsed.hostname}/*`; const granted = await chrome.permissions.request({origins: [pattern]}); if (!granted) throw new Error('Permission to connect to the backend was not granted'); }
    catch (e) { $('status').textContent = e.message || 'Invalid backend URL'; $('scan').disabled = false; return; }
  }
  try {
    const all = await chrome.management.getAll();
    const extensions = all.filter(x => x.type === 'extension' && x.enabled && x.id !== chrome.runtime.id).map(classify);
    const report = {source:'chrome_extension', scanned_at:new Date().toISOString(), extensions, sites:[]};
    const high = extensions.filter(x=>x.risk_level==='high').length;
    $('results').innerHTML = extensions.map(x=>`<article class="item"><b>${escapeHtml(x.name)}</b><p class="${x.risk_level}">${x.risk_level.toUpperCase()} RISK · ${x.permissions.length} declared permissions</p><p>${escapeHtml(x.reason)}</p></article>`).join('') || '<p class="muted">No other enabled extensions found.</p>';
    const token = $('token').value.trim();
    if (token) {
      const response = await fetch(`${base}/api/v1/permissions/report`, {method:'POST',headers:{'Content-Type':'application/json','Authorization':`Bearer ${token}`},body:JSON.stringify(report)});
      if (!response.ok) throw new Error((await response.json().catch(()=>({}))).detail || `Sync failed (${response.status})`);
      const result = await response.json(); $('status').textContent = `Synced ${result.extensions_audited} extensions · ${result.high_risk} high risk`;
    } else $('status').textContent = `Local audit complete · ${extensions.length} extensions · ${high} high risk. Add a token to sync.`;
  } catch (e) { $('status').textContent = e.message || 'Audit failed'; }
  finally {$('scan').disabled = false;}
}
function escapeHtml(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
$('scan').addEventListener('click',run);
chrome.storage.local.get(['api','token'],v=>{if(v.api)$('api').value=v.api;if(v.token)$('token').value=v.token;});
$('api').addEventListener('change',()=>chrome.storage.local.set({api:$('api').value}));
$('token').addEventListener('change',()=>chrome.storage.local.set({token:$('token').value}));
