import React, { useState } from 'react';
import { X, FileText, CheckCircle2, Hash, Calendar, Layers, HardDrive, ExternalLink } from 'lucide-react';
import { openFileInNativeApp } from '../api';

export default function DocumentModal({ doc, onClose }) {
  const [isOpening, setIsOpening] = useState(false);
  const [openNotice, setOpenNotice] = useState(null);

  if (!doc) return null;

  const handleOpenInApp = async () => {
    setIsOpening(true);
    setOpenNotice(null);
    try {
      await openFileInNativeApp({
        filePath: doc.path || null,
        projectId: doc.projectId || doc.project_id || null,
        fileName: doc.name,
      });
      setOpenNotice({ type: 'success', text: `Opened ${doc.name}` });
      setTimeout(() => setOpenNotice(null), 3000);
    } catch (err) {
      setOpenNotice({ type: 'error', text: `Could not open file: ${err.message}` });
      setTimeout(() => setOpenNotice(null), 4000);
    } finally {
      setIsOpening(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container doc-preview-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <FileText size={20} className="modal-icon" />
            <div>
              <h3 className="modal-title">{doc.name}</h3>
              <span className="modal-subtitle">Document Metadata & Retrieval Summary</span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleOpenInApp}
              disabled={isOpening}
              title={`Open ${doc.name}`}
            >
              <ExternalLink size={13} className={isOpening ? 'spin-anim' : ''} />
              <span>{isOpening ? 'Opening...' : 'Open File'}</span>
            </button>
            <button className="modal-close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="modal-body">
          <div className="doc-meta-grid">
            <div className="meta-card">
              <span className="meta-label">Status</span>
              <span className="meta-value status-badge status-ready">
                <CheckCircle2 size={13} />
                {doc.status || 'READY'}
              </span>
            </div>
            <div className="meta-card">
              <span className="meta-label">File Type</span>
              <span className="meta-value uppercase">{doc.type || 'Document'}</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">File Size</span>
              <span className="meta-value">{doc.size}</span>
            </div>
            <div className="meta-card">
              <span className="meta-label">Last Modified</span>
              <span className="meta-value">{doc.updatedAt || 'Recent'}</span>
            </div>
          </div>

          <div className="doc-section">
            <h4 className="doc-section-heading">Document Executive Summary</h4>
            <div className="doc-summary-box">
              <p>{doc.summary || 'Summary generated during canonical ingestion pipeline.'}</p>
            </div>
          </div>

          <div className="doc-section">
            <h4 className="doc-section-heading">Provenance & Canonical Storage</h4>
            <div className="provenance-info-box">
              <div className="prov-row">
                <Layers size={14} />
                <span>Lineage: <strong>Document &rarr; Section Hierarchy &rarr; Dense Chunks</strong></span>
              </div>
              <div className="prov-row">
                <HardDrive size={14} />
                <span>Indexed in: <strong>Qdrant Collection & SQLite Registry</strong></span>
              </div>
              <div className="prov-row">
                <Hash size={14} />
                <span>Document ID: <code>{doc.id}</code></span>
              </div>
            </div>
          </div>
        </div>

        <div className="modal-footer" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <button
              type="button"
              className="btn btn-primary"
              onClick={handleOpenInApp}
              disabled={isOpening}
              title={`Open ${doc.name}`}
            >
              <ExternalLink size={14} className={isOpening ? 'spin-anim' : ''} />
              <span>{isOpening ? 'Opening...' : 'Open File'}</span>
            </button>
            {openNotice && (
              <span style={{ marginLeft: 12, fontSize: '0.82rem', color: openNotice.type === 'error' ? '#ef4444' : '#10b981', fontWeight: 500 }}>
                {openNotice.text}
              </span>
            )}
          </div>
          <button className="btn btn-secondary" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
