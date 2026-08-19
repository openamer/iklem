"""The iklem web UI — a single self-contained HTML page served at /.

This is a browser-based client for the same JSON API the desktop app uses.
It is served by the iklem server itself, so `iklem --server` gives you a
working web app at http://127.0.0.1:8787/ with no build step.
"""

from __future__ import annotations

WEB_UI_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>iklem</title>
<style>
:root{--bg:#0d1117;--bg2:#161b22;--bg3:#1c2128;--bd:#30363d;--tx:#e6edf3;--dim:#8b949e;--ac:#58a6ff;--ac2:#1f6feb;--ub:#1f6feb;--ab:#21262d;--dg:#f85149}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--tx);overflow:hidden}
.app{display:flex;height:100vh}
.sidebar{width:260px;background:var(--bg2);border-right:1px solid var(--bd);display:flex;flex-direction:column;flex-shrink:0}
.brand{display:flex;align-items:center;gap:8px;padding:16px;font-size:18px;font-weight:600}
.brand-mark{color:var(--ac)}
.new-session{margin:0 12px 12px;padding:8px 12px;background:var(--ac2);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:13px}
.new-session:hover{background:var(--ac)}
.session-list{flex:1;overflow-y:auto;padding:0 8px}
.session-item{padding:8px 12px;border-radius:6px;cursor:pointer;font-size:13px;color:var(--dim);margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.session-item:hover{background:var(--bg3);color:var(--tx)}
.session-item.active{background:var(--bg3);color:var(--tx)}
.main{flex:1;display:flex;flex-direction:column}
.chat-header{display:flex;align-items:center;justify-content:space-between;padding:12px 20px;border-bottom:1px solid var(--bd);font-size:14px;font-weight:600}
.status{font-size:12px;color:var(--dim);font-weight:400}
.status.ok{color:#3fb950}
.status.err{color:var(--dg)}
.messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:12px}
.msg{max-width:70%;padding:10px 14px;border-radius:12px;line-height:1.5;font-size:14px;white-space:pre-wrap;word-wrap:break-word}
.msg.user{align-self:flex-end;background:var(--ub);color:#fff;border-bottom-right-radius:4px}
.msg.assistant{align-self:flex-start;background:var(--ab);border-bottom-left-radius:4px}
.msg.error{align-self:flex-start;background:#2d1518;color:var(--dg)}
.msg.assistant p{margin:0 0 8px}.msg.assistant p:last-child{margin-bottom:0}
.msg.assistant h1,.msg.assistant h2,.msg.assistant h3{margin:12px 0 6px;font-size:1.1em}
.msg.assistant ul{margin:0 0 8px;padding-left:20px}
.msg.assistant code{background:rgba(110,118,129,.4);padding:2px 5px;border-radius:4px;font-family:Consolas,monospace;font-size:13px}
.msg.assistant pre{background:#0d1117;border:1px solid var(--bd);border-radius:8px;padding:12px;overflow-x:auto;margin:8px 0}
.msg.assistant pre code{background:transparent;padding:0;font-size:13px;white-space:pre}
.msg.assistant a{color:var(--ac);text-decoration:none}
.msg.assistant strong{font-weight:600}
.tok-kw{color:#ff7b72}.tok-str{color:#a5d6ff}.tok-com{color:#8b949e;font-style:italic}.tok-num{color:#79c0ff}
.ok-mark{color:#3fb950;font-weight:600}.err-mark{color:#f85149;font-weight:600}
.code-block{position:relative;margin:8px 0}.code-lang{position:absolute;top:6px;right:10px;font-size:11px;color:var(--dim);text-transform:uppercase;letter-spacing:.5px}.code-block pre{padding-top:24px}
.msg.assistant table{border-collapse:collapse;margin:8px 0;width:100%;font-size:13px}.msg.assistant th,.msg.assistant td{border:1px solid var(--bd);padding:6px 10px;text-align:left}.msg.assistant th{background:var(--bg3);font-weight:600}
.msg.assistant blockquote{border-left:3px solid var(--ac);padding-left:12px;margin:8px 0;color:var(--dim)}.msg.assistant blockquote p{margin:0}
.msg.assistant hr{border:none;border-top:1px solid var(--bd);margin:12px 0}
.msg.assistant ol{margin:0 0 8px;padding-left:20px}
.msg.assistant ul.task-list{list-style:none;padding-left:0}.msg.assistant .task-item{display:flex;align-items:center;gap:6px}.msg.assistant .task-box{color:var(--ac)}.msg.assistant .task-item.done{color:var(--dim);text-decoration:line-through}
.composer{display:flex;gap:8px;padding:12px 20px;border-top:1px solid var(--bd)}
.composer textarea{flex:1;resize:none;background:var(--bg3);color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;font-size:14px;font-family:inherit;max-height:160px}
.composer textarea:focus{outline:none;border-color:var(--ac)}
.send{padding:0 20px;background:var(--ac2);color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px}
.send:hover{background:var(--ac)}
.send:disabled{opacity:.5}
.welcome{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;gap:12px;padding:40px}.welcome-mark{font-size:48px;color:var(--ac);line-height:1}.welcome h1{font-size:28px;font-weight:600;color:var(--tx)}.welcome p{color:var(--dim);font-size:15px;max-width:420px}.welcome-hints{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:12px}.welcome-hints span{background:var(--bg3);border:1px solid var(--bd);border-radius:16px;padding:6px 14px;font-size:13px;color:var(--dim)}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand"><span class="brand-mark">◆</span><span>iklem</span></div>
    <button id="new-session" class="new-session">+ New session</button>
    <nav class="session-list" id="session-list"></nav>
  </aside>
  <main class="main">
    <header class="chat-header"><span id="chat-title">iklem</span><span id="status" class="status">connecting…</span></header>
    <div class="messages" id="messages"><div class="welcome" id="welcome"><div class="welcome-mark">◆</div><h1>iklem</h1><p>Ein selbstverbessernder KI-Agent — forged, not cloned.</p><div class="welcome-hints"><span>Frag nach dem Datum oder der Uhrzeit</span><span>Lass mich Dateien lesen oder Code ausführen</span><span>Suche im Web oder öffne eine App</span></div></div></div>
    <footer class="composer">
      <textarea id="input" rows="1" placeholder="Message iklem…"></textarea>
      <button id="send" class="send">Send</button>
    </footer>
  </main>
</div>
<script>
const $=id=>document.getElementById(id);
let currentSessionId=null;
async function api(path,opts={}){const r=await fetch(path,{headers:{'Content-Type':'application/json'},...opts});return r.json();}
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
function inline(t){let s=esc(t);s=s.replace(/`([^`]+)`/g,'<code>$1</code>');s=s.replace(/\\*\\*([^*]+)\\*\\*/g,'<strong>$1</strong>');s=s.replace(/\\*([^*]+)\\*/g,'<em>$1</em>');s=s.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g,'<a href="$2" target="_blank">$1</a>');s=s.replace(/✓/g,'<span class="ok-mark">✓</span>');s=s.replace(/✗/g,'<span class="err-mark">✗</span>');return s;}
function md(m){const ls=m.split('\\n');let h='',ic=false,cb=[],cl='',il=false,lt='ul',iq=false,tb=[];const cll=()=>{if(il){h+='</'+lt+'>';il=false;}};const clq=()=>{if(iq){h+='</blockquote>';iq=false;}};const ftb=()=>{if(tb.length){const hd=tb[0],bd=tb.slice(1);let t='<table><thead><tr>';hd.forEach(c=>t+='<th>'+inline(c)+'</th>');t+='</tr></thead><tbody>';bd.forEach(r=>{const cs=r.filter(c=>c.trim()!=='');if(cs.length>0&&cs.every(c=>/^:?-{2,}:?$/.test(c.trim())))return;t+='<tr>';r.forEach(c=>t+='<td>'+inline(c)+'</td>');t+='</tr>';});t+='</tbody></table>';h+=t;tb=[];}};for(const line of ls){const f=line.trim().match(/^```(\\w*)/);if(f){if(ic){const lb=cl?'<span class="code-lang">'+esc(cl)+'</span>':'';h+='<div class="code-block">'+lb+'<pre><code>'+hl(cb.join('\\n'),cl)+'</code></pre></div>';cb=[];cl='';ic=false;}else{cll();clq();ftb();ic=true;cl=f[1]||'';}continue;}if(ic){cb.push(line);continue;}if(line.includes('|')){cll();clq();tb.push(line.split('|').map(c=>c.trim()));continue;}else if(tb.length){ftb();}const hh=line.match(/^(#{1,4})\\s+(.*)/);if(hh){cll();clq();h+='<h'+hh[1].length+'>'+inline(hh[2])+'</h'+hh[1].length+'>';continue;}if(/^\\s*(-{3,}|\\*{3,})\\s*$/.test(line)){cll();clq();h+='<hr>';continue;}const q=line.match(/^\\s*>\\s?(.*)/);if(q){cll();if(!iq){h+='<blockquote>';iq=true;}h+='<p>'+inline(q[1])+'</p>';continue;}else if(iq){clq();}const tk=line.match(/^\\s*[-*]\\s+\\[([ xX])\\]\\s+(.*)/);if(tk){if(!il||lt!=='ul'){cll();h+='<ul class="task-list">';il=true;lt='ul';}const ck=tk[1].toLowerCase()==='x';h+='<li class="task-item'+(ck?' done':'')+'"><span class="task-box">'+(ck?'☑':'☐')+'</span>'+inline(tk[2])+'</li>';continue;}const ol=line.match(/^\\s*\\d+\\.\\s+(.*)/);if(ol){if(!il||lt!=='ol'){cll();h+='<ol>';il=true;lt='ol';}h+='<li>'+inline(ol[1])+'</li>';continue;}const li=line.match(/^\\s*[-*]\\s+(.*)/);if(li){if(!il||lt!=='ul'){cll();h+='<ul>';il=true;lt='ul';}h+='<li>'+inline(li[1])+'</li>';continue;}if(line.trim()===''){cll();clq();continue;}cll();clq();h+='<p>'+inline(line)+'</p>';}if(ic){const lb=cl?'<span class="code-lang">'+esc(cl)+'</span>':'';h+='<div class="code-block">'+lb+'<pre><code>'+hl(cb.join('\\n'),cl)+'</code></pre></div>';}ftb();cll();clq();return h;}
function add(role,content){const w=$('welcome');if(w)w.remove();const d=document.createElement('div');d.className='msg '+role;if(role==='assistant')d.innerHTML=md(content);else d.textContent=content;$('messages').appendChild(d);$('messages').scrollTop=$('messages').scrollHeight;return d;}
function setStatus(t,c){const e=$('status');e.textContent=t;e.className='status '+(c||'');}
async function loadSessions(){try{const ss=await api('/sessions');const l=$('session-list');l.innerHTML='';ss.forEach(s=>{const it=document.createElement('div');it.className='session-item'+(s.id===currentSessionId?' active':'');it.textContent=s.title;it.onclick=()=>open(s.id,s.title);l.appendChild(it);});if(!currentSessionId&&ss.length>0){open(ss[0].id,ss[0].title);}}catch(e){setStatus('offline','err');}}
function showWelcome(){const m=$('messages');m.innerHTML='';const w=document.createElement('div');w.className='welcome';w.id='welcome';w.innerHTML='<div class="welcome-mark">◆</div><h1>iklem</h1><p>Ein selbstverbessernder KI-Agent — forged, not cloned.</p><div class="welcome-hints"><span>Frag nach dem Datum oder der Uhrzeit</span><span>Lass mich Dateien lesen oder Code ausführen</span><span>Suche im Web oder öffne eine App</span></div>';m.appendChild(w);}
async function open(id,title){currentSessionId=id;$('chat-title').textContent=title;$('messages').innerHTML='';try{const ms=await api('/sessions/'+id);if(ms.length===0){showWelcome();}else{ms.forEach(m=>add(m.role,m.content));}}catch(e){add('error','Failed to load');}loadSessions();}
async function newSession(){try{const r=await api('/sessions',{method:'POST',body:JSON.stringify({title:'New session'})});currentSessionId=r.id;$('chat-title').textContent='New session';showWelcome();loadSessions();}catch(e){setStatus('offline','err');}}
async function send(){const inp=$('input');const t=inp.value.trim();if(!t||!currentSessionId)return;add('user',t);inp.value='';$('send').disabled=true;const p=add('assistant','');let acc='';try{const r=await fetch('/sessions/'+currentSessionId+'/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});if(!r.ok)throw new Error('HTTP '+r.status);const rd=r.body.getReader();const dc=new TextDecoder();while(true){const{done,value}=await rd.read();if(done)break;acc+=dc.decode(value,{stream:true});p.innerHTML=md(acc);$('messages').scrollTop=$('messages').scrollHeight;}if(!acc){p.className='msg error';p.textContent='(empty)';}}catch(e){p.className='msg error';p.textContent='Server unreachable';}$('send').disabled=false;}
async function health(){try{const h=await api('/health');if(h.ok)setStatus('online','ok');}catch(e){setStatus('offline','err');}}
$('send').onclick=send;$('new-session').onclick=newSession;
$('input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
(async()=>{await health();await loadSessions();if(!currentSessionId)await newSession();})();
</script>
</body>
</html>
"""
