// A dependency-free Markdown renderer for the chat UI.
// Supports: code blocks (```lang) with a language label, inline code (`),
// bold (**), italics (*), headings (#), ordered/unordered lists, task lists
// (- [ ] / - [x]), tables, blockquotes (>), horizontal rules (---), and
// links. Safe: escapes HTML first. Status markers (✓/✗) are colorized.

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
  // status markers: ✓ green, ✗ red
  s = s.replace(/✓/g, '<span class="ok-mark">✓</span>');
  s = s.replace(/✗/g, '<span class="err-mark">✗</span>');
  return s;
}

// A lightweight syntax highlighter for code blocks.
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

function renderTable(rows) {
  // rows: array of arrays of cell strings (already split on |)
  if (rows.length < 2) return null;
  const header = rows[0];
  const body = rows.slice(1);
  let html = '<table><thead><tr>';
  for (const cell of header) {
    html += `<th>${renderInline(cell.trim())}</th>`;
  }
  html += '</tr></thead><tbody>';
  for (const row of body) {
    // skip separator rows like |---|---|
    if (row.every((c) => /^:?-{2,}:?$/.test(c.trim()))) continue;
    html += '<tr>';
    for (const cell of row) {
      html += `<td>${renderInline(cell.trim())}</td>`;
    }
    html += '</tr>';
  }
  html += '</tbody></table>';
  return html;
}

function renderMarkdown(md) {
  const lines = md.split('\n');
  let html = '';
  let inCode = false;
  let codeBuf = [];
  let codeLang = '';
  let inList = false;
  let listType = 'ul';
  let inQuote = false;
  let tableBuf = [];

  const closeList = () => {
    if (inList) {
      html += `</${listType}>`;
      inList = false;
    }
  };
  const closeQuote = () => {
    if (inQuote) {
      html += '</blockquote>';
      inQuote = false;
    }
  };
  const flushTable = () => {
    if (tableBuf.length) {
      const t = renderTable(tableBuf);
      if (t) html += t;
      tableBuf = [];
    }
  };

  for (const line of lines) {
    // code block
    const fence = line.trim().match(/^```(\w*)/);
    if (fence) {
      if (inCode) {
        const label = codeLang ? `<span class="code-lang">${escapeHtml(codeLang)}</span>` : '';
        html += `<div class="code-block">${label}<pre><code>${highlightCode(codeBuf.join('\n'), codeLang)}</code></pre></div>`;
        codeBuf = [];
        codeLang = '';
        inCode = false;
      } else {
        closeList();
        closeQuote();
        flushTable();
        inCode = true;
        codeLang = fence[1] || '';
      }
      continue;
    }
    if (inCode) {
      codeBuf.push(line);
      continue;
    }

    // table row (contains | and not a code fence)
    if (line.includes('|')) {
      closeList();
      closeQuote();
      tableBuf.push(line.split('|').map((c) => c.trim()));
      continue;
    } else if (tableBuf.length) {
      flushTable();
    }

    // heading
    const h = line.match(/^(#{1,4})\s+(.*)/);
    if (h) {
      closeList();
      closeQuote();
      const level = h[1].length;
      html += `<h${level}>${renderInline(h[2])}</h${level}>`;
      continue;
    }

    // horizontal rule
    if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) {
      closeList();
      closeQuote();
      html += '<hr>';
      continue;
    }

    // blockquote
    const q = line.match(/^\s*>\s?(.*)/);
    if (q) {
      closeList();
      if (!inQuote) {
        html += '<blockquote>';
        inQuote = true;
      }
      html += `<p>${renderInline(q[1])}</p>`;
      continue;
    } else if (inQuote) {
      closeQuote();
    }

    // task list item
    const task = line.match(/^\s*[-*]\s+\[([ xX])\]\s+(.*)/);
    if (task) {
      if (!inList || listType !== 'ul') {
        closeList();
        html += '<ul class="task-list">';
        inList = true;
        listType = 'ul';
      }
      const checked = task[1].toLowerCase() === 'x';
      const box = checked ? '☑' : '☐';
      html += `<li class="task-item${checked ? ' done' : ''}"><span class="task-box">${box}</span>${renderInline(task[2])}</li>`;
      continue;
    }

    // ordered list item
    const oli = line.match(/^\s*\d+\.\s+(.*)/);
    if (oli) {
      if (!inList || listType !== 'ol') {
        closeList();
        html += '<ol>';
        inList = true;
        listType = 'ol';
      }
      html += `<li>${renderInline(oli[1])}</li>`;
      continue;
    }

    // unordered list item
    const li = line.match(/^\s*[-*]\s+(.*)/);
    if (li) {
      if (!inList || listType !== 'ul') {
        closeList();
        html += '<ul>';
        inList = true;
        listType = 'ul';
      }
      html += `<li>${renderInline(li[1])}</li>`;
      continue;
    }

    // blank line
    if (line.trim() === '') {
      closeList();
      closeQuote();
      continue;
    }

    // paragraph
    closeList();
    closeQuote();
    html += `<p>${renderInline(line)}</p>`;
  }

  if (inCode) {
    const label = codeLang ? `<span class="code-lang">${escapeHtml(codeLang)}</span>` : '';
    html += `<div class="code-block">${label}<pre><code>${highlightCode(codeBuf.join('\n'), codeLang)}</code></pre></div>`;
  }
  flushTable();
  closeList();
  closeQuote();
  return html;
}
