// iklem desktop — renderer logic.
// Talks to the iklem HTTP server via fetch.

const API = window.iklem.serverUrl;
let currentSessionId = null;

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
  div.textContent = content;
  $('messages').appendChild(div);
  $('messages').scrollTop = $('messages').scrollHeight;
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
      list.appendChild(item);
    });
  } catch (e) {
    setStatus('offline', 'err');
  }
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

async function send() {
  const input = $('input');
  const text = input.value.trim();
  if (!text || !currentSessionId) return;
  addMessage('user', text);
  input.value = '';
  $('send').disabled = true;
  try {
    const res = await api('/sessions/' + currentSessionId + '/chat', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
    if (res.reply) {
      addMessage('assistant', res.reply);
    } else if (res.error) {
      addMessage('error', res.error);
    }
  } catch (e) {
    addMessage('error', 'Server unreachable');
  }
  $('send').disabled = false;
}

async function checkHealth() {
  try {
    const h = await api('/health');
    if (h.ok) setStatus('online', 'ok');
  } catch (e) {
    setStatus('offline', 'err');
  }
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

$('settings-btn').onclick = () => $('settings-modal').classList.remove('hidden');
$('settings-close').onclick = () => $('settings-modal').classList.add('hidden');

// Init
(async () => {
  await checkHealth();
  await loadSessions();
  if (!currentSessionId) await newSession();
})();
