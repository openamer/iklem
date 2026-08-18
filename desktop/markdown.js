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

function renderMarkdown(md) {
  const lines = md.split('\n');
  let html = '';
  let inCode = false;
  let codeBuf = [];
  let inList = false;

  const closeList = () => {
    if (inList) {
      html += '</ul>';
      inList = false;
    }
  };

  for (const line of lines) {
    // code block
    if (line.trim().startsWith('```')) {
      if (inCode) {
        html += '<pre><code>' + escapeHtml(codeBuf.join('\n')) + '</code></pre>';
        codeBuf = [];
        inCode = false;
      } else {
        closeList();
        inCode = true;
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
    html += '<pre><code>' + escapeHtml(codeBuf.join('\n')) + '</code></pre>';
  }
  closeList();
  return html;
}
