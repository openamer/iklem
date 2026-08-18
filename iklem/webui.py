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
.composer{display:flex;gap:8px;padding:12px 20px;border-top:1px solid var(--bd)}
.composer textarea{flex:1;resize:none;background:var(--bg3);color:var(--tx);border:1px solid var(--bd);border-radius:8px;padding:10px 12px;font-size:14px;font-family:inherit;max-height:160px}
.composer textarea:focus{outline:none;border-color:var(--ac)}
.send{padding:0 20px;background:var(--ac2);color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:14px}
.send:hover{background:var(--ac)}
.send:disabled{opacity:.5}
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
    <div class="messages" id="messages"></div>
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
function inline(t){let s=esc(t);s=s.replace(/`([^`]+)`/g,'<code>$1</code>');s=s.replace(/\\*\\*([^*]+)\\*\\*/g,'<strong>$1</strong>');s=s.replace(/\\*([^*]+)\\*/g,'<em>$1</em>');s=s.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g,'<a href="$2" target="_blank">$1</a>');return s;}
function hl(code,lang){const e=esc(code);if(!lang)return e;const l=lang.toLowerCase();if(l==='python'||l==='py')return e.replace(/(&quot;.*?&quot;|&#39;.*?&#39;)/g,'<span class="tok-str">$1</span>').replace(/\\b(def|class|return|import|from|if|else|elif|for|while|try|except|with|as|in|not|and|or|None|True|False|lambda|yield|pass|break|continue|raise|global|nonlocal|assert|del|is)\\b/g,'<span class="tok-kw">$1</span>').replace(/(#.*)$/gm,'<span class="tok-com">$1</span>').replace(/\\b(\\d+\\.?\\d*)\\b/g,'<span class="tok-num">$1</span>');if(l==='javascript'||l==='js'||l==='typescript'||l==='ts')return e.replace(/(&quot;.*?&quot;|&#39;.*?&#39;|`.*?`)/g,'<span class="tok-str">$1</span>').replace(/\\b(const|let|var|function|return|if|else|for|while|new|class|extends|import|from|export|default|async|await|try|catch|throw|typeof|instanceof|in|of|null|undefined|true|false|this|super)\\b/g,'<span class="tok-kw">$1</span>').replace(/(\\/\\/.*)$/gm,'<span class="tok-com">$1</span>').replace(/\\b(\\d+\\.?\\d*)\\b/g,'<span class="tok-num">$1</span>');if(l==='bash'||l==='sh'||l==='shell')return e.replace(/(&quot;.*?&quot;|&#39;.*?&#39;)/g,'<span class="tok-str">$1</span>').replace(/(#.*)$/gm,'<span class="tok-com">$1</span>').replace(/\\b(echo|cd|ls|git|npm|pip|python|node|curl|mkdir|rm|cp|mv|cat|export|sudo|docker|kubectl)\\b/g,'<span class="tok-kw">$1</span>');return e;}
function md(m){const ls=m.split('\\n');let h='',ic=false,cb=[],cl='',il=false;const cll=()=>{if(il){h+='</ul>';il=false;}};for(const line of ls){const f=line.trim().match(/^```(\\w*)/);if(f){if(ic){h+='<pre><code>'+hl(cb.join('\\n'),cl)+'</code></pre>';cb=[];cl='';ic=false;}else{cll();ic=true;cl=f[1]||'';}continue;}if(ic){cb.push(line);continue;}const hh=line.match(/^(#{1,4})\\s+(.*)/);if(hh){cll();h+='<h'+hh[1].length+'>'+inline(hh[2])+'</h'+hh[1].length+'>';continue;}const li=line.match(/^\\s*[-*]\\s+(.*)/);if(li){if(!il){h+='<ul>';il=true;}h+='<li>'+inline(li[1])+'</li>';continue;}if(line.trim()===''){cll();continue;}cll();h+='<p>'+inline(line)+'</p>';}if(ic){h+='<pre><code>'+hl(cb.join('\\n'),cl)+'</code></pre>';}cll();return h;}
function add(role,content){const d=document.createElement('div');d.className='msg '+role;if(role==='assistant')d.innerHTML=md(content);else d.textContent=content;$('messages').appendChild(d);$('messages').scrollTop=$('messages').scrollHeight;return d;}
function setStatus(t,c){const e=$('status');e.textContent=t;e.className='status '+(c||'');}
async function loadSessions(){try{const ss=await api('/sessions');const l=$('session-list');l.innerHTML='';ss.forEach(s=>{const it=document.createElement('div');it.className='session-item'+(s.id===currentSessionId?' active':'');it.textContent=s.title;it.onclick=()=>open(s.id,s.title);l.appendChild(it);});}catch(e){setStatus('offline','err');}}
async function open(id,title){currentSessionId=id;$('chat-title').textContent=title;$('messages').innerHTML='';try{const ms=await api('/sessions/'+id);ms.forEach(m=>add(m.role,m.content));}catch(e){add('error','Failed to load');}loadSessions();}
async function newSession(){try{const r=await api('/sessions',{method:'POST',body:JSON.stringify({title:'New session'})});currentSessionId=r.id;$('chat-title').textContent='New session';$('messages').innerHTML='';loadSessions();}catch(e){setStatus('offline','err');}}
async function send(){const inp=$('input');const t=inp.value.trim();if(!t||!currentSessionId)return;add('user',t);inp.value='';$('send').disabled=true;const p=add('assistant','');let acc='';try{const r=await fetch('/sessions/'+currentSessionId+'/stream',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t})});if(!r.ok)throw new Error('HTTP '+r.status);const rd=r.body.getReader();const dc=new TextDecoder();while(true){const{done,value}=await rd.read();if(done)break;acc+=dc.decode(value,{stream:true});p.innerHTML=md(acc);$('messages').scrollTop=$('messages').scrollHeight;}if(!acc){p.className='msg error';p.textContent='(empty)';}}catch(e){p.className='msg error';p.textContent='Server unreachable';}$('send').disabled=false;}
async function health(){try{const h=await api('/health');if(h.ok)setStatus('online','ok');}catch(e){setStatus('offline','err');}}
$('send').onclick=send;$('new-session').onclick=newSession;
$('input').addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
(async()=>{await health();await loadSessions();if(!currentSessionId)await newSession();})();
</script>
</body>
</html>
"""
