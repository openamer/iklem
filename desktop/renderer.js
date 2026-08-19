// iklem desktop — renderer logic.
// Talks to the iklem HTTP server via fetch.

const API = window.iklem.serverUrl;
let currentSessionId = null;
let contextTargetId = null;

const $ = (id) => document.getElementById(id);

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  return res.json();
}

function setStatus(text, cls) {
  const el = $('status');
  el.textContent = text;
  el.className = 'status ' + (cls || '');
}

function addMessage(role, content) {
  // Hide the welcome screen once the first message appears.
  const welcome = $('welcome');
  if (welcome) welcome.remove();
  const div = document.createElement('div');
  div.className = 'msg ' + role;
  if (role === 'assistant') {
    div.innerHTML = renderMarkdown(content);
  } else {
    div.textContent = content;
  }
  $('messages').appendChild(div);
  $('messages').scrollTop = $('messages').scrollHeight;
  return div;
}

async function loadSessions() {
  try {
    const sessions = await api('/sessions');
    const list = $('session-list');
    list.innerHTML = '';
    sessions.forEach((s) => {
      const item = document.createElement('div');
      item.className = 'session-item' + (s.id === currentSessionId ? ' active' : '');
      item.textContent = s.title;
      item.onclick = () => openSession(s.id, s.title);
      item.oncontextmenu = (e) => {
        e.preventDefault();
        contextTargetId = s.id;
        showContextMenu(e.clientX, e.clientY);
      };
      list.appendChild(item);
    });
    // If no session is selected but sessions exist, open the first one
    // (instead of creating yet another "New session").
    if (!currentSessionId && sessions.length > 0) {
      openSession(sessions[0].id, sessions[0].title);
    }
  } catch (e) {
    setStatus('offline', 'err');
  }
}

function showContextMenu(x, y) {
  const menu = $('context-menu');
  menu.classList.remove('hidden');
  menu.style.left = x + 'px';
  menu.style.top = y + 'px';
}

function hideContextMenu() {
  $('context-menu').classList.add('hidden');
}

function showWelcome() {
  const messages = $('messages');
  messages.innerHTML = '';
  const w = document.createElement('div');
  w.className = 'welcome';
  w.id = 'welcome';
  w.innerHTML =
    '<div class="welcome-mark">◆</div>' +
    '<h1>iklem</h1>' +
    '<p>Ein selbstverbessernder KI-Agent — forged, not cloned.</p>' +
    '<div class="welcome-hints">' +
    '<span>Frag nach dem Datum oder der Uhrzeit</span>' +
    '<span>Lass mich Dateien lesen oder Code ausführen</span>' +
    '<span>Suche im Web oder öffne eine App</span>' +
    '</div>';
  messages.appendChild(w);
}

async function openSession(id, title) {
  currentSessionId = id;
  $('chat-title').textContent = title;
  $('messages').innerHTML = '';
  try {
    const messages = await api('/sessions/' + id);
    if (messages.length === 0) {
      showWelcome();
    } else {
      messages.forEach((m) => addMessage(m.role, m.content));
    }
  } catch (e) {
    addMessage('error', 'Failed to load session');
  }
  loadSessions();
}

async function newSession() {
  try {
    const res = await api('/sessions', {
      method: 'POST',
      body: JSON.stringify({ title: 'New session' }),
    });
    currentSessionId = res.id;
    $('chat-title').textContent = 'New session';
    showWelcome();
    loadSessions();
  } catch (e) {
    setStatus('offline', 'err');
  }
}

async function renameSession(id) {
  const title = prompt('Rename session:', '');
  if (!title) return;
  await api('/sessions/' + id, {
    method: 'PATCH',
    body: JSON.stringify({ title }),
  });
  loadSessions();
  if (id === currentSessionId) $('chat-title').textContent = title;
}

async function deleteSession(id) {
  if (!confirm('Delete this session?')) return;
  await api('/sessions/' + id, { method: 'DELETE' });
  if (id === currentSessionId) {
    currentSessionId = null;
    $('messages').innerHTML = '';
    $('chat-title').textContent = 'iklem';
  }
  loadSessions();
}

async function send() {
  const input = $('input');
  const text = input.value.trim();
  if (!text || !currentSessionId) return;
  addMessage('user', text);
  input.value = '';
  $('send').disabled = true;
  const pending = addMessage('assistant', '');
  let acc = '';
  try {
    const res = await fetch(API + '/sessions/' + currentSessionId + '/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      acc += decoder.decode(value, { stream: true });
      pending.innerHTML = renderMarkdown(acc);
      $('messages').scrollTop = $('messages').scrollHeight;
    }
    if (!acc) {
      pending.className = 'msg error';
      pending.textContent = '(empty reply)';
    }
  } catch (e) {
    pending.className = 'msg error';
    pending.textContent = 'Server unreachable';
  }
  $('send').disabled = false;
  $('messages').scrollTop = $('messages').scrollHeight;
}

async function checkHealth() {
  try {
    const h = await api('/health');
    if (h.ok) setStatus('online', 'ok');
  } catch (e) {
    setStatus('offline', 'err');
  }
}

async function loadConfig() {
  try {
    const cfg = await api('/config');
    if (cfg.IKLEM_OLLAMA_MODEL) $('cfg-model').value = cfg.IKLEM_OLLAMA_MODEL;
    if (cfg.IKLEM_OLLAMA_URL) $('cfg-url').value = cfg.IKLEM_OLLAMA_URL;
  } catch (e) {}
}

// Wire up UI
$('send').onclick = send;
$('new-session').onclick = newSession;
$('input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

$('settings-btn').onclick = () => {
  loadConfig();
  $('settings-modal').classList.remove('hidden');
};
$('settings-close').onclick = () => $('settings-modal').classList.add('hidden');
$('settings-save').onclick = async () => {
  await api('/config', {
    method: 'POST',
    body: JSON.stringify({
      IKLEM_OLLAMA_MODEL: $('cfg-model').value,
      IKLEM_OLLAMA_URL: $('cfg-url').value,
    }),
  });
  $('settings-modal').classList.add('hidden');
};

// Theme toggle (persisted in localStorage)
function applyTheme(light) {
  document.body.classList.toggle('light', light);
  $('theme-btn').textContent = light ? '☀️ Theme' : '🌙 Theme';
  localStorage.setItem('iklem-theme', light ? 'light' : 'dark');
}
$('theme-btn').onclick = () => {
  applyTheme(!document.body.classList.contains('light'));
};
// Restore saved theme
if (localStorage.getItem('iklem-theme') === 'light') applyTheme(true);

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'n') {
    e.preventDefault();
    newSession();
  }
  if (e.ctrlKey && e.key === 'l') {
    e.preventDefault();
    $('input').focus();
  }
});

$('ctx-rename').onclick = () => {
  hideContextMenu();
  if (contextTargetId) renameSession(contextTargetId);
};
$('ctx-delete').onclick = () => {
  hideContextMenu();
  if (contextTargetId) deleteSession(contextTargetId);
};
document.addEventListener('click', (e) => {
  if (!$('context-menu').contains(e.target)) hideContextMenu();
});

// Init
(async () => {
  await checkHealth();
  await loadSessions();
  // Only create a new session if there are none at all.
  if (!currentSessionId) await newSession();
})();
