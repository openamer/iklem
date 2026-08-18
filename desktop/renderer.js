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

async function openSession(id, title) {
  currentSessionId = id;
  $('chat-title').textContent = title;
  $('messages').innerHTML = '';
  try {
    const messages = await api('/sessions/' + id);
    messages.forEach((m) => addMessage(m.role, m.content));
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
    $('messages').innerHTML = '';
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
  if (!currentSessionId) await newSession();
})();
