// A minimal, dependency-free Markdown renderer for the chat UI.
// Supports: code blocks (```), inline code (`), bold (**), italics (*),
// headings (#), lists (-/*), and links. Safe: escapes HTML first.

function escapeHtml(s) {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function renderInline(text) {
  let s = escapeHtml(text);
  // inline code
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  // bold
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  // italics
  s = s.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  // links [text](url)
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
  return s;
}

// A lightweight syntax highlighter for code blocks. Detects the language
// from the ```lang fence and applies token classes for common languages.
function highlightCode(code, lang) {
  const escaped = escapeHtml(code);
  if (!lang) return escaped;

  const l = lang.toLowerCase();
  if (l === 'python' || l === 'py') {
    return escaped
      .replace(/(&quot;.*?&quot;|&#39;.*?&#39;)/g, '<span class="tok-str">$1</span>')
      .replace(/\b(def|class|return|import|from|if|else|elif|for|while|try|except|with|as|in|not|and|or|None|True|False|lambda|yield|pass|break|continue|raise|global|nonlocal|assert|del|is)\b/g, '<span class="tok-kw">$1</span>')
      .replace(/(#.*)$/gm, '<span class="tok-com">$1</span>')
      .replace(/\b(\d+\.?\d*)\b/g, '<span class="tok-num">$1</span>');
  }
  if (l === 'javascript' || l === 'js' || l === 'typescript' || l === 'ts') {
    return escaped
      .replace(/(&quot;.*?&quot;|&#39;.*?&#39;|`.*?`)/g, '<span class="tok-str">$1</span>')
      .replace(/\b(const|let|var|function|return|if|else|for|while|new|class|extends|import|from|export|default|async|await|try|catch|throw|typeof|instanceof|in|of|null|undefined|true|false|this|super)\b/g, '<span class="tok-kw">$1</span>')
      .replace(/(\/\/.*)$/gm, '<span class="tok-com">$1</span>')
      .replace(/\b(\d+\.?\d*)\b/g, '<span class="tok-num">$1</span>');
  }
  if (l === 'bash' || l === 'sh' || l === 'shell') {
    return escaped
      .replace(/(&quot;.*?&quot;|&#39;.*?&#39;)/g, '<span class="tok-str">$1</span>')
      .replace(/(#.*)$/gm, '<span class="tok-com">$1</span>')
      .replace(/\b(echo|cd|ls|git|npm|pip|python|node|curl|mkdir|rm|cp|mv|cat|export|sudo|docker|kubectl)\b/g, '<span class="tok-kw">$1</span>');
  }
  return escaped;
}

function renderMarkdown(md) {
  const lines = md.split('\n');
  let html = '';
  let inCode = false;
  let codeBuf = [];
  let codeLang = '';
  let inList = false;

  const closeList = () => {
    if (inList) {
      html += '</ul>';
      inList = false;
    }
  };

  for (const line of lines) {
    // code block
    const fence = line.trim().match(/^```(\w*)/);
    if (fence) {
      if (inCode) {
        html += '<pre><code>' + highlightCode(codeBuf.join('\n'), codeLang) + '</code></pre>';
        codeBuf = [];
        codeLang = '';
        inCode = false;
      } else {
        closeList();
        inCode = true;
        codeLang = fence[1] || '';
      }
      continue;
    }
    if (inCode) {
      codeBuf.push(line);
      continue;
    }

    // heading
    const h = line.match(/^(#{1,4})\s+(.*)/);
    if (h) {
      closeList();
      const level = h[1].length;
      html += `<h${level}>${renderInline(h[2])}</h${level}>`;
      continue;
    }

    // list item
    const li = line.match(/^\s*[-*]\s+(.*)/);
    if (li) {
      if (!inList) {
        html += '<ul>';
        inList = true;
      }
      html += `<li>${renderInline(li[1])}</li>`;
      continue;
    }

    // blank line
    if (line.trim() === '') {
      closeList();
      continue;
    }

    // paragraph
    closeList();
    html += `<p>${renderInline(line)}</p>`;
  }

  if (inCode) {
    html += '<pre><code>' + highlightCode(codeBuf.join('\n'), codeLang) + '</code></pre>';
  }
  closeList();
  return html;
}
