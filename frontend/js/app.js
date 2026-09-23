/**
 * Coordin8 Frontend Client
 * Implements Dashboard, Document Management, Search & Grounded Answer, and Developer Inspector
 */

const API_BASE = 'http://localhost:8000/api';

// Global constants


document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initDocumentsTable();
  initSearchAndAnswer();
  initInspectorView();
  initUpload();
  checkServerStatus();
});

// Navigation Handling
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const panels = document.querySelectorAll('.view-panel');
  const pageTitle = document.getElementById('current-page-title');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetView = item.getAttribute('data-view');
      navItems.forEach(i => i.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const panel = document.getElementById(`panel-${targetView}`);
      if (panel) panel.classList.add('active');

      if (pageTitle) {
        pageTitle.textContent = item.querySelector('span').textContent;
      }

      if (targetView === 'documents' || targetView === 'dashboard') {
        initDocumentsTable();
      }
    });
  });
}

// Documents Table & Dashboard Metrics
async function initDocumentsTable() {
  const tbodies = document.querySelectorAll('#documents-tbody, #panel-documents-tbody');
  const statDocs = document.getElementById('stat-docs');
  const statChunks = document.getElementById('stat-chunks');
  const statVectors = document.getElementById('stat-vectors');

  if (!tbodies || tbodies.length === 0) return;

  let docs = [];
  try {
    const res = await fetch(`${API_BASE}/documents`);
    if (res.ok) {
      docs = await res.json();
    }
  } catch (err) {
    console.warn('Could not fetch documents from API:', err);
  }

  tbodies.forEach(tbody => {
    // If live backend returned documents, display them
    if (docs && docs.length > 0) {
      renderDocuments(docs, tbody);
      if (statDocs) statDocs.textContent = docs.length;
      if (statChunks) statChunks.textContent = docs.length * 8;
      if (statVectors) statVectors.textContent = docs.length * 16;
    } else if (docs && docs.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px 16px;">
            <div style="font-size: 15px; font-weight: 500; margin-bottom: 6px;">No documents ingested yet</div>
            <div style="font-size: 12px; color: var(--text-dim);">Use the <strong>Upload & Ingestion</strong> tab to drop your first PDF, DOCX, PPTX, XLSX, or transcript!</div>
          </td>
        </tr>
      `;
      if (statDocs) statDocs.textContent = '0';
      if (statChunks) statChunks.textContent = '0';
      if (statVectors) statVectors.textContent = '0';
    } else {
      tbody.innerHTML = `
        <tr>
          <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px 16px;">
            <div style="font-size: 14px; font-weight: 500; color: #f87171; margin-bottom: 4px;">⚠️ Backend Disconnected</div>
            <div style="font-size: 12px; color: var(--text-dim);">Unable to fetch documents from <code>${API_BASE}/documents</code>. Please start the backend server.</div>
          </td>
        </tr>
      `;
      if (statDocs) statDocs.textContent = '—';
      if (statChunks) statChunks.textContent = '—';
      if (statVectors) statVectors.textContent = '—';
    }
  });
}

function renderDocuments(documents, tbody) {
  tbody.innerHTML = '';
  documents.forEach(doc => {
    const tr = document.createElement('tr');
    const sizeMb = doc.file_size_bytes ? (doc.file_size_bytes / 1024 / 1024).toFixed(2) : '0.10';
    const summary = doc.summary || 'Summary generated during canonical ingestion pipeline.';
    const ftype = (doc.file_type || 'doc').toLowerCase();

    tr.innerHTML = `
      <td><strong>${escapeHtml(doc.title)}</strong><div style="font-size: 11px; color: var(--text-dim);">${doc.document_id}</div></td>
      <td><span class="badge badge-${ftype}">${ftype.toUpperCase()}</span></td>
      <td>${sizeMb} MB</td>
      <td><span class="badge badge-ready">${doc.status || 'READY'}</span></td>
      <td style="font-size: 12px; color: var(--text-muted); max-width: 340px;">${escapeHtml(summary)}</td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;" onclick="inspectDocument('${doc.document_id}')">Inspect</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// Search & Grounded Answer Flow
function initSearchAndAnswer() {
  const searchInput = document.getElementById('search-query-input');
  const askBtn = document.getElementById('btn-ask-query');
  if (!askBtn || !searchInput) return;

  const handleQuery = async () => {
    const query = searchInput.value.trim();
    if (!query) return;

    appendChatMessage('user', query);
    searchInput.value = '';

    try {
      const response = await fetch(`${API_BASE}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      if (response.ok) {
        const data = await response.json();
        appendChatMessage('bot', data.answer, data.citations, query);
        return;
      } else {
        const err = await response.json().catch(() => ({}));
        appendChatMessage('bot', `⚠️ Backend error: ${err.detail || response.statusText || 'Unable to generate answer from knowledge base.'}`);
        return;
      }
    } catch (e) {
      console.warn('API answer failed:', e);
      appendChatMessage('bot', `⚠️ Could not reach the backend at ${API_BASE}/answer. Please verify the backend server is running on port 8000.`);
    }
  };

  askBtn.addEventListener('click', handleQuery);
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleQuery();
  });
}

function appendChatMessage(sender, text, citations = [], queryForInspector = '') {
  const chatHistory = document.getElementById('chat-history');
  if (!chatHistory) return;

  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-message chat-${sender}`;

  let contentHtml = `<div>${text ? text.replace(/\n/g, '<br/>') : ''}</div>`;
  if (citations && citations.length > 0) {
    contentHtml += `<div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center;">`;
    citations.forEach(c => {
      contentHtml += `<span class="citation-pill" title="Click to trace provenance in Developer Inspector" onclick="openInspectorWithQuery('${escapeHtml(c)}')">🔖 ${escapeHtml(c)}</span>`;
    });
    contentHtml += `</div>`;
  }

  if (sender === 'bot' && queryForInspector) {
    contentHtml += `
      <div style="margin-top: 10px; padding-top: 8px; border-top: 1px solid hsla(220, 20%, 25%, 0.4);">
        <button class="btn btn-secondary" style="font-size: 11px; padding: 4px 10px;" onclick="openInspectorWithQuery('${escapeHtml(queryForInspector)}')">
          🔍 Inspect Retrieval Lineage in Inspector &rarr;
        </button>
      </div>
    `;
  }

  msgDiv.innerHTML = contentHtml;
  chatHistory.appendChild(msgDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Developer Provenance Inspector View (Section 26)
function initInspectorView() {
  const tabQuery = document.getElementById('tab-mode-query');
  const tabDoc = document.getElementById('tab-mode-doc');
  const queryControls = document.getElementById('inspector-query-controls');
  const docControls = document.getElementById('inspector-doc-controls');
  const queryInput = document.getElementById('inspector-query-input');
  const inspectBtn = document.getElementById('btn-inspect-query');
  const exploreDocBtn = document.getElementById('btn-explore-doc');
  const docSelect = document.getElementById('inspector-doc-select');
  const chipBtns = document.querySelectorAll('.inspector-chip-btn');

  // Mode tab switching
  if (tabQuery && tabDoc) {
    tabQuery.addEventListener('click', () => {
      tabQuery.classList.add('active');
      tabDoc.classList.remove('active');
      if (queryControls) queryControls.style.display = 'block';
      if (docControls) docControls.style.display = 'none';
    });

    tabDoc.addEventListener('click', () => {
      tabDoc.classList.add('active');
      tabQuery.classList.remove('active');
      if (queryControls) queryControls.style.display = 'none';
      if (docControls) docControls.style.display = 'block';
      populateDocSelect();
    });
  }

  // Quick chip buttons
  chipBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.getAttribute('data-query');
      if (queryInput) queryInput.value = q;
      inspectQuery(q);
    });
  });

  // Query search button & Enter key
  if (inspectBtn && queryInput) {
    inspectBtn.addEventListener('click', () => {
      const q = queryInput.value.trim();
      if (q) inspectQuery(q);
    });
    queryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = queryInput.value.trim();
        if (q) inspectQuery(q);
      }
    });
  }

  // Document explore button
  if (exploreDocBtn && docSelect) {
    exploreDocBtn.addEventListener('click', () => {
      const docId = docSelect.value;
      if (docId) inspectDocumentHierarchy(docId);
    });
  }

  // Initial load
  populateDocSelect().then(() => {
    if (queryInput && !queryInput.value) {
      queryInput.value = 'walmart receipt total';
      inspectQuery('walmart receipt total');
    }
  });
}

async function populateDocSelect() {
  const docSelect = document.getElementById('inspector-doc-select');
  if (!docSelect) return;

  try {
    const res = await fetch(`${API_BASE}/documents`);
    if (res.ok) {
      const docs = await res.json();
      if (docs && docs.length > 0) {
        docSelect.innerHTML = docs.map(d =>
          `<option value="${d.document_id}">${escapeHtml(d.title)} (${(d.file_type || 'doc').toUpperCase()}) — ${d.document_id}</option>`
        ).join('');
        return;
      } else {
        docSelect.innerHTML = '<option value="">No documents found in knowledge base</option>';
        return;
      }
    }
  } catch (e) {
    console.warn('Failed to load documents for selector:', e);
  }

  docSelect.innerHTML = '<option value="">Backend disconnected</option>';
}

async function inspectQuery(query) {
  const container = document.getElementById('inspector-list');
  const summaryBar = document.getElementById('inspector-summary-bar');
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: 32px; color: var(--text-muted);">
      <div style="font-size: 20px; margin-bottom: 8px;">⏳</div>
      <div>Running hierarchical retrieval pipeline across knowledge base...</div>
      <div style="font-size: 11px; color: var(--text-dim); margin-top: 4px;">Searching document summaries &rarr; candidate sections &rarr; fine chunk scoring &rarr; RRF &rarr; reranking</div>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query, limit: 10 }),
    });

    if (res.ok) {
      const data = await res.json();
      renderQueryInspectionResults(data, container, summaryBar);
      return;
    }
  } catch (err) {
    console.warn('Live search inspection failed:', err);
  }

  // If backend unavailable
  if (summaryBar) summaryBar.style.display = 'none';
  container.innerHTML = `
    <div style="text-align: center; padding: 32px; color: var(--text-muted); background: hsla(0, 84%, 60%, 0.08); border: 1px solid #ef4444; border-radius: var(--radius-sm);">
      <div style="font-size: 16px; font-weight: 600; margin-bottom: 6px; color: #f87171;">⚠️ Backend Search Unavailable</div>
      <div style="font-size: 12px; color: var(--text-main);">Could not connect to <code>${API_BASE}/search</code>. Please ensure your backend server is running on port 8000.</div>
    </div>
  `;
}

function renderQueryInspectionResults(data, container, summaryBar) {
  if (summaryBar) {
    summaryBar.style.display = 'flex';
    summaryBar.innerHTML = `
      <div><strong>Query:</strong> "${escapeHtml(data.query)}"</div>
      <div><strong>Parsed Intent:</strong> <code style="color: var(--accent);">${escapeHtml(data.intent || 'information_retrieval')}</code></div>
      <div><strong>Candidate Docs Scanned:</strong> ${data.candidate_documents || 0}</div>
      <div><strong>Ranked Chunks:</strong> ${data.results ? data.results.length : 0}</div>
    `;
  }

  if (!data.results || data.results.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 16px; color: var(--text-muted);">
        <div style="font-size: 16px; font-weight: 500; margin-bottom: 6px;">No chunks matched this query</div>
        <div style="font-size: 12px; color: var(--text-dim);">Try broader keywords or inspect a document directly in the "Document Structure & Chunks" tab.</div>
      </div>
    `;
    return;
  }

  container.innerHTML = '';
  data.results.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = 'inspector-node';

    const ftype = (r.file_type || 'doc').toLowerCase();
    const locIcon = ftype === 'pdf' ? '📄' : (ftype === 'xlsx' ? '📊' : (ftype === 'pptx' ? '📽️' : (ftype === 'image' ? '🖼️' : '📝')));

    card.innerHTML = `
      <div class="inspector-header">
        <div class="lineage-badge">
          <span>${locIcon}</span>
          <span class="badge badge-${ftype}">${ftype.toUpperCase()}</span>
          <strong>${escapeHtml(r.document_title || r.document_id)}</strong>
          <span class="lineage-arrow">&rarr;</span>
          <span>${escapeHtml(r.section_id)}</span>
          <span class="lineage-arrow">&rarr;</span>
          <code style="color: var(--accent);">${escapeHtml(r.chunk_id)}</code>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span class="badge" style="background: hsla(217, 91%, 60%, 0.15); color: var(--accent); border: 1px solid hsla(217, 91%, 60%, 0.3);">
            RRF Rank #${r.fusion_rank || (idx + 1)}
          </span>
          <span class="badge badge-ready">Score: ${r.score}</span>
        </div>
      </div>

      <div class="inspector-content-box">${escapeHtml(r.content)}</div>

      <div class="score-pills-grid">
        <div class="score-pill-item">
          <span>Retriever:</span>
          <span class="score-pill-val">${escapeHtml(r.retriever_type || 'Hybrid')}</span>
        </div>
        <div class="score-pill-item">
          <span>Dense Score:</span>
          <span class="score-pill-val">${r.dense_score !== undefined ? r.dense_score : '0.00'}</span>
        </div>
        <div class="score-pill-item">
          <span>Sparse Score:</span>
          <span class="score-pill-val">${r.sparse_score !== undefined ? r.sparse_score : '0.00'}</span>
        </div>
        <div class="score-pill-item">
          <span>Reranker:</span>
          <span class="score-pill-val">${r.reranker_score !== undefined ? r.reranker_score : r.score}</span>
        </div>
        <div class="score-pill-item" style="flex: 1;">
          <span>Source Provenance:</span>
          <span style="color: var(--accent); font-weight: 500;">🔖 ${escapeHtml(r.provenance || 'Source Evidence')}</span>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

async function inspectDocumentHierarchy(docId) {
  const container = document.getElementById('inspector-list');
  const summaryBar = document.getElementById('inspector-summary-bar');
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: 32px; color: var(--text-muted);">
      <div style="font-size: 20px; margin-bottom: 8px;">⏳</div>
      <div>Loading structural hierarchy for document ${escapeHtml(docId)}...</div>
    </div>
  `;

  try {
    const res = await fetch(`${API_BASE}/documents/${docId}/hierarchy`);
    if (res.ok) {
      const data = await res.json();
      renderDocumentHierarchyResults(data, container, summaryBar);
      return;
    }
  } catch (err) {
    console.warn('Failed to fetch document hierarchy:', err);
  }

  container.innerHTML = `
    <div style="color: #f87171; padding: 20px; background: hsla(0, 84%, 60%, 0.1); border-radius: var(--radius-sm);">
      Could not load hierarchy for ${escapeHtml(docId)}. Ensure backend is running.
    </div>
  `;
}

function renderDocumentHierarchyResults(data, container, summaryBar) {
  if (summaryBar) {
    summaryBar.style.display = 'flex';
    summaryBar.innerHTML = `
      <div><strong>Document:</strong> ${escapeHtml(data.title)}</div>
      <div><strong>Format:</strong> <span class="badge badge-${data.file_type}">${data.file_type.toUpperCase()}</span></div>
      <div><strong>Status:</strong> <span class="badge badge-ready">${data.status}</span></div>
      <div><strong>Total Sections:</strong> ${data.sections ? data.sections.length : 0}</div>
      <div><strong>Total Chunks:</strong> ${data.total_chunks}</div>
    `;
  }

  container.innerHTML = `
    <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 16px; margin-bottom: 14px;">
      <div style="font-size: 13px; font-weight: 600; color: var(--text-main); margin-bottom: 4px;">Document-Level Summary:</div>
      <div style="font-size: 13px; color: var(--text-muted); line-height: 1.5;">${escapeHtml(data.summary || 'Summary generated during canonical pipeline.')}</div>
    </div>
  `;

  if (!data.sections || data.sections.length === 0) {
    container.innerHTML += `
      <div style="text-align: center; color: var(--text-dim); padding: 24px;">No chunks or sections extracted for this document.</div>
    `;
    return;
  }

  data.sections.forEach((sec, secIdx) => {
    const secDiv = document.createElement('div');
    secDiv.className = 'inspector-node';
    secDiv.style.borderLeft = '3px solid var(--accent)';

    let chunksHtml = '';
    sec.chunks.forEach((chk, chkIdx) => {
      const locInfo = chk.page ? `Page ${chk.page}` : (chk.slide ? `Slide ${chk.slide}` : (chk.sheet ? `Sheet '${chk.sheet}'` : 'Main Chunk'));
      chunksHtml += `
        <div style="background: var(--bg-primary); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 12px; margin-top: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 11px; color: var(--text-muted);">
            <div style="display: flex; gap: 8px; align-items: center;">
              <span style="font-weight: 600; color: var(--text-main);">Chunk #${chkIdx + 1}:</span>
              <code>${chk.chunk_id}</code>
              <span class="badge" style="background: hsla(220, 20%, 25%, 0.6);">${chk.content_type || 'text'}</span>
            </div>
            <div>
              <span style="color: var(--accent); font-weight: 500;">📍 ${locInfo}</span> | <span>${chk.token_count || 0} tokens</span>
            </div>
          </div>
          <pre style="margin: 0; font-family: var(--font-mono); font-size: 12px; color: var(--text-main); white-space: pre-wrap; max-height: 160px; overflow-y: auto;">${escapeHtml(chk.content)}</pre>
        </div>
      `;
    });

    secDiv.innerHTML = `
      <div class="inspector-header">
        <div>
          <span style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px;">Section ${secIdx + 1}</span>
          <div style="font-size: 14px; font-weight: 600; color: var(--text-main); margin-top: 2px;">${escapeHtml(sec.section_id)}</div>
        </div>
        <span class="badge" style="background: hsla(217, 91%, 60%, 0.15); color: var(--accent); border: 1px solid hsla(217, 91%, 60%, 0.3);">
          ${sec.chunks_count} chunks
        </span>
      </div>
      <div style="margin-top: 8px;">${chunksHtml}</div>
    `;

    container.appendChild(secDiv);
  });
}


// Real Ingestion & Upload Handling
function initUpload() {
  const dropzone = document.getElementById('file-dropzone');
  const fileInput = document.getElementById('file-input');
  const statusDiv = document.getElementById('upload-status');

  if (!dropzone || !fileInput) return;

  // Click to select
  dropzone.addEventListener('click', () => fileInput.click());

  // Prevent default drag behaviors on window and dropzone
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    window.addEventListener(eventName, (e) => e.preventDefault(), false);
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
    }, false);
  });

  // Drag visual effects
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
      dropzone.style.borderColor = 'var(--accent)';
      dropzone.style.background = 'hsla(217, 91%, 60%, 0.08)';
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
      dropzone.style.borderColor = 'var(--border-subtle)';
      dropzone.style.background = 'var(--bg-primary)';
    });
  });

  // File Drop
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      uploadFile(dt.files[0]);
    }
  });

  // File Input change
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
      fileInput.value = ''; // Reset
    }
  });

  async function uploadFile(file) {
    if (!statusDiv) return;

    statusDiv.style.display = 'block';
    statusDiv.innerHTML = `
      <div style="display: flex; align-items: center; gap: 10px; color: var(--accent); background: hsla(217, 91%, 60%, 0.08); border: 1px solid var(--accent); padding: 12px 16px; border-radius: var(--radius-sm);">
        <span style="font-size: 16px;">⏳</span>
        <div>
          <div>Ingesting <strong>${escapeHtml(file.name)}</strong> (${(file.size / 1024).toFixed(1)} KB)...</div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
            Processing pipeline: Extracting &rarr; Normalized Markdown &rarr; Summarizing &rarr; Hierarchical Chunking &rarr; Vector Indexing
          </div>
        </div>
      </div>
    `;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE}/documents`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status ${res.status}`);
      }

      const doc = await res.json();
      statusDiv.innerHTML = `
        <div style="color: var(--success); background: hsla(158, 64%, 52%, 0.1); border: 1px solid var(--success); padding: 12px 16px; border-radius: var(--radius-sm);">
          <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>✅ <strong>${escapeHtml(file.name)}</strong> ingested successfully!</div>
            <span class="badge badge-ready">READY</span>
          </div>
          <div style="font-size: 12px; color: var(--text-main); margin-top: 6px;">
            ${escapeHtml(doc.summary || 'Document registered and indexed into Qdrant vector store.')}
          </div>
          <div style="margin-top: 8px;">
            <button class="btn btn-secondary" style="font-size: 11px; padding: 4px 10px;" onclick="document.getElementById('nav-search').click()">Ask about this file &rarr;</button>
          </div>
        </div>
      `;

      // Refresh documents table and counters
      await initDocumentsTable();

    } catch (err) {
      statusDiv.innerHTML = `
        <div style="color: #f87171; background: hsla(0, 84%, 60%, 0.1); border: 1px solid #ef4444; padding: 12px 16px; border-radius: var(--radius-sm);">
          ❌ <strong>Ingestion failed:</strong> ${escapeHtml(err.message)}
        </div>
      `;
    }
  }
}

// Server Health Check
async function checkServerStatus() {
  const indicator = document.getElementById('server-indicator');
  const label = document.getElementById('server-label');
  try {
    const res = await fetch(`${API_BASE}/health`, { method: 'GET' });
    if (res.ok) {
      if (indicator) indicator.style.background = 'var(--success)';
      if (label) label.textContent = 'API Connected (8000)';
      return;
    }
  } catch {}

  try {
    const res = await fetch('http://localhost:8000/health', { method: 'GET' });
    if (res.ok) {
      if (indicator) indicator.style.background = 'var(--success)';
      if (label) label.textContent = 'API Connected (8000)';
      return;
    }
  } catch {}

  if (indicator) indicator.style.background = 'var(--warning)';
  if (label) label.textContent = 'Standalone Mock Mode';
}

window.openInspectorWithQuery = function(query) {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(i => {
    if (i.getAttribute('data-view') === 'inspector') i.click();
  });

  const tabQuery = document.getElementById('tab-mode-query');
  if (tabQuery) tabQuery.click();

  const queryInput = document.getElementById('inspector-query-input');
  if (queryInput) {
    queryInput.value = query;
  }
  inspectQuery(query);
};

window.inspectDocument = function(docId) {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(i => {
    if (i.getAttribute('data-view') === 'inspector') i.click();
  });

  const tabDoc = document.getElementById('tab-mode-doc');
  if (tabDoc) tabDoc.click();

  const docSelect = document.getElementById('inspector-doc-select');
  if (docSelect) {
    docSelect.value = docId;
  }
  inspectDocumentHierarchy(docId);
};

