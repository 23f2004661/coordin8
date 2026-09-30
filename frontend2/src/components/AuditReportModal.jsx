import React, { useState } from 'react';
import {
  X,
  Sparkles,
  HardDrive,
  Copy,
  Check,
  FileText,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileSpreadsheet,
  Link2,
  ChevronRight,
  TrendingUp,
  Building2,
  Briefcase,
  Layers,
  Code,
  ExternalLink,
} from 'lucide-react';
import { openFileInNativeApp } from '../api';

export default function AuditReportModal({
  isOpen,
  onClose,
  project,
  onAcceptCandidate,
}) {
  const [activeViewTab, setActiveViewTab] = useState('breakdown'); // 'breakdown' | 'markdown'
  const [copiedMd, setCopiedMd] = useState(false);
  const [isOpeningNative, setIsOpeningNative] = useState(false);
  const [openNotice, setOpenNotice] = useState(null);

  if (!isOpen || !project) return null;

  const aiAnalysis = project.ai_analysis || {};
  const folderPath =
    project.folder_path ||
    `C:\\Users\\ssrin\\Desktop\\Coordin8 Home\\${project.name}`;
  const latestReportPath =
    aiAnalysis.latestReportPath ||
    aiAnalysis.reportFile ||
    `${folderPath}\\audit_reports\\latest_audit_report.md`;

  const reportMarkdown =
    aiAnalysis.markdownReport ||
    `# Coordin8 AI Deliverable & Progress Audit Report\n\n- **Project:** ${project.name}\n- **Overall Completion:** ${aiAnalysis.overallCompletion || project.progress || 0}%\n- **Health:** ${aiAnalysis.health || 'on_track'}\n\n## Executive Summary\n${aiAnalysis.executiveSummary || 'No summary available.'}`;

  const deliverables = project.deliverables || [];
  const discovered = project.discovered_deliverables || aiAnalysis.discoveredDeliverables || [];
  const auditedMap = new Map();
  if (Array.isArray(aiAnalysis.deliverableAudits)) {
    for (const a of aiAnalysis.deliverableAudits) {
      if (a.id && a.id !== 'None') auditedMap.set(String(a.id), a);
      if (a.title) auditedMap.set(String(a.title).toLowerCase().trim(), a);
    }
  }

  const handleOpenInDesktop = async () => {
    setIsOpeningNative(true);
    setOpenNotice(null);
    try {
      await openFileInNativeApp({
        filePath: latestReportPath,
        projectId: project.id || project.project_id,
        fileName: 'latest_audit_report.md',
      });
      setOpenNotice({ type: 'success', msg: 'Opened file' });
      setTimeout(() => setOpenNotice(null), 3000);
    } catch (err) {
      setOpenNotice({ type: 'error', msg: `Could not open report: ${err.message}` });
      setTimeout(() => setOpenNotice(null), 4000);
    } finally {
      setIsOpeningNative(false);
    }
  };

  const handleOpenFile = async (fileName) => {
    try {
      await openFileInNativeApp({
        projectId: project.id || project.project_id,
        fileName,
      });
    } catch (err) {
      alert(`Could not open ${fileName}: ${err.message}`);
    }
  };

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(reportMarkdown);
    setCopiedMd(true);
    setTimeout(() => setCopiedMd(false), 2000);
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-container audit-report-modal-box"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="modal-header audit-modal-header">
          <div className="audit-header-title-row">
            <div className="audit-sparkle-badge">
              <Sparkles size={18} />
            </div>
            <div>
              <div className="audit-title-meta-line">
                <span className="audit-project-name">{project.name}</span>
                <span className="audit-code-chip">{project.code}</span>
                <span className={`project-type-tag ${project.project_type === 'client' ? 'type-client' : 'type-internal'}`}>
                  {project.project_type === 'client' ? (
                    <>
                      <Building2 size={11} />
                      <span>Client: {project.client_name || 'External'}</span>
                    </>
                  ) : (
                    <>
                      <Briefcase size={11} />
                      <span>Internal</span>
                    </>
                  )}
                </span>
                <span className={`health-status-badge health-${aiAnalysis.health || 'on_track'}`}>
                  {aiAnalysis.health === 'on_track' ? '● On Track' : aiAnalysis.health === 'at_risk' ? '▲ At Risk' : '✕ Delayed'}
                </span>
              </div>
              <h3 className="modal-title">AI Deliverable & Progress Audit Log</h3>
            </div>
          </div>
          <div className="audit-modal-header-actions">
            <button
              type="button"
              className="btn btn-secondary btn-sm open-desktop-btn"
              onClick={handleOpenInDesktop}
              disabled={isOpeningNative}
              title="Open this audit report directly in your default markdown or text editor"
            >
              <ExternalLink size={13} className={isOpeningNative ? 'spin-anim' : ''} />
              <span>{isOpeningNative ? 'Opening...' : 'Open File'}</span>
            </button>
            <button className="modal-close-btn" onClick={onClose}>
              <X size={18} />
            </button>
          </div>
        </div>

        {/* Modal Navigation Tabs */}
        <div className="audit-modal-nav-tabs">
          <button
            type="button"
            className={`audit-nav-tab ${activeViewTab === 'breakdown' ? 'active' : ''}`}
            onClick={() => setActiveViewTab('breakdown')}
          >
            <TrendingUp size={14} />
            <span>Executive Briefing & Verified Deliverables</span>
          </button>
          <button
            type="button"
            className={`audit-nav-tab ${activeViewTab === 'markdown' ? 'active' : ''}`}
            onClick={() => setActiveViewTab('markdown')}
          >
            <Code size={14} />
            <span>Raw Markdown Audit File</span>
          </button>
        </div>

        {/* Tab 1: Formatted Breakdown */}
        {activeViewTab === 'breakdown' && (
          <div className="audit-modal-content-scroll">
            {/* Top Metrics Row */}
            <div className="audit-summary-metrics-grid">
              <div className="audit-metric-card">
                <span className="metric-card-label">Overall Completion</span>
                <span className="metric-card-val highlight">
                  {aiAnalysis.overallCompletion || project.progress || 0}%
                </span>
                <div className="metric-card-progress-bar">
                  <div
                    className="metric-card-progress-fill"
                    style={{
                      width: `${aiAnalysis.overallCompletion || project.progress || 0}%`,
                      backgroundColor: project.color || '#6366f1',
                    }}
                  />
                </div>
              </div>

              <div className="audit-metric-card">
                <span className="metric-card-label">Execution Health</span>
                <span className={`metric-card-val health-text-${aiAnalysis.health || 'on_track'}`}>
                  {aiAnalysis.health === 'on_track' ? 'On Track' : aiAnalysis.health === 'at_risk' ? 'At Risk' : 'Delayed'}
                </span>
                <span className="metric-card-sub">
                  {aiAnalysis.lastAnalyzedAt
                    ? `Audited ${new Date(aiAnalysis.lastAnalyzedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                    : 'Just now'}
                </span>
              </div>

              <div className="audit-metric-card">
                <span className="metric-card-label">Deliverables Audited</span>
                <span className="metric-card-val">{deliverables.length}</span>
                <span className="metric-card-sub">
                  {deliverables.filter((d) => d.status === 'completed').length} completed
                </span>
              </div>

              <div className="audit-metric-card">
                <span className="metric-card-label">Discovered Milestones</span>
                <span className="metric-card-val amber">{discovered.length}</span>
                <span className="metric-card-sub">Mined from emails & specs</span>
              </div>
            </div>

            {/* Strategic Problem Statement */}
            <div className="audit-section-block">
              <h4 className="audit-section-heading">Strategic Problem Statement</h4>
              <p className="audit-problem-text">
                {project.problem_statement || project.description || 'No strategic problem statement recorded.'}
              </p>
            </div>

            {/* Executive Status Briefing */}
            <div className="audit-section-block briefing-block">
              <h4 className="audit-section-heading">
                <Sparkles size={14} className="sparkle-indigo" />
                <span>Executive Status Briefing</span>
              </h4>
              <p className="briefing-content">
                {aiAnalysis.executiveSummary || 'Cross-referencing deliverables against documents and client communications.'}
              </p>
            </div>

            {/* Evidence-Anchored Deliverables List */}
            <div className="audit-section-block">
              <h4 className="audit-section-heading">
                <span>Deliverables Proof-of-Work & Evidence Breakdown</span>
                <span className="heading-count">({deliverables.length})</span>
              </h4>

              {deliverables.length === 0 ? (
                <div className="audit-empty-delivs">
                  <p>No deliverables tracked yet for this project.</p>
                </div>
              ) : (
                <div className="audit-delivs-list">
                  {deliverables.map((deliv) => {
                    const audit =
                      deliv.aiAudit ||
                      auditedMap.get(String(deliv.id)) ||
                      auditedMap.get(String(deliv.title).toLowerCase().trim()) ||
                      {};
                    const isDone = deliv.status === 'completed';

                    return (
                      <div key={deliv.id || deliv.title} className="audit-deliv-card">
                        <div className="audit-deliv-header">
                          <div className="audit-deliv-title-group">
                            <span className={`deliv-status-pill status-${deliv.status}`}>
                              {deliv.status}
                            </span>
                            <h5 className="audit-deliv-title">{deliv.title}</h5>
                          </div>
                          <div className="audit-deliv-prog-chip">
                            <span>{deliv.progress || 0}%</span>
                          </div>
                        </div>

                        {deliv.description && (
                          <p className="audit-deliv-desc">{deliv.description}</p>
                        )}

                        {/* Audit Verification Block */}
                        <div className="audit-deliv-proof-box">
                          <div className="proof-box-header">
                            <Sparkles size={12} className="proof-sparkle" />
                            <span className="proof-title">AI Proof Assessment:</span>
                          </div>
                          <p className="proof-text">
                            {audit.evidence || 'No conclusive evidence found in current documents or communications.'}
                          </p>

                          {audit.evidenceFiles && audit.evidenceFiles.length > 0 && (
                            <div className="proof-files-row">
                              <span className="proof-files-label">Cited Artifacts:</span>
                              {audit.evidenceFiles.map((fn, fIdx) => (
                                <button
                                  key={fIdx}
                                  type="button"
                                  className="evidence-file-chip clickable"
                                  onClick={() => handleOpenFile(fn)}
                                  title={`Open ${fn} directly in its native desktop application`}
                                >
                                  <FileSpreadsheet size={11} />
                                  <span>{fn}</span>
                                  <ExternalLink size={10} className="chip-ext-icon" />
                                </button>
                              ))}
                            </div>
                          )}

                          {audit.blockers && (
                            <div className="proof-blocker-row">
                              <AlertCircle size={12} className="blocker-icon" />
                              <span>Blocker: {audit.blockers}</span>
                            </div>
                          )}
                        </div>

                        <div className="audit-deliv-footer">
                          <span className="deliv-meta-item">
                            Due: <strong>{deliv.dueDate || 'Flexible'}</strong>
                          </span>
                          <span className="deliv-meta-item">
                            Owner: <strong>{deliv.owner || 'Team'}</strong>
                          </span>
                          {deliv.source && (
                            <span className="deliv-meta-item">
                              Source: <strong>{deliv.source}</strong>
                            </span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Discovered Deliverables Section */}
            {discovered.length > 0 && (
              <div className="audit-section-block discovered-section">
                <h4 className="audit-section-heading">
                  <Sparkles size={14} className="sparkle-amber" />
                  <span>Candidate Milestones Mined from Ingested Inputs ({discovered.length})</span>
                </h4>
                <div className="discovered-audit-grid">
                  {discovered.map((c, cIdx) => (
                    <div key={cIdx} className="discovered-audit-card">
                      <div className="discovered-audit-header">
                        <span className={`priority-pill priority-${c.priority || 'medium'}`}>
                          {c.priority || 'medium'}
                        </span>
                        <span className="discovered-source-pill">
                          {c.source === 'email' ? 'From Client Email' : 'From Meeting / PRD'}
                        </span>
                      </div>
                      <h5 className="discovered-audit-title">{c.title}</h5>
                      <p className="discovered-audit-desc">{c.description}</p>
                      {c.sourceEvidence && (
                        <div className="discovered-citation">
                          <Link2 size={11} />
                          <span>Citation: "{c.sourceEvidence}"</span>
                        </div>
                      )}
                      <div className="discovered-audit-footer">
                        <span className="suggested-date">Target: {c.suggestedDueDate || 'Upcoming'}</span>
                        {onAcceptCandidate && (
                          <button
                            type="button"
                            className="btn btn-primary btn-xs accept-btn"
                            onClick={() => onAcceptCandidate(c)}
                          >
                            <CheckCircle2 size={12} />
                            <span>Add to Timeline</span>
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Raw Markdown Report */}
        {activeViewTab === 'markdown' && (
          <div className="audit-modal-content-scroll">
            <div className="audit-markdown-controls-row">
              <span className="markdown-file-name-label">
                File: <code>latest_audit_report.md</code>
              </span>
              <button
                type="button"
                className="btn btn-secondary btn-xs"
                onClick={handleCopyMarkdown}
              >
                {copiedMd ? <Check size={12} className="text-green" /> : <Copy size={12} />}
                <span>{copiedMd ? 'Copied Markdown' : 'Copy Full Markdown'}</span>
              </button>
            </div>
            <pre className="audit-markdown-code-block">{reportMarkdown}</pre>
          </div>
        )}

        {/* Modal Footer */}
        <div className="modal-footer audit-modal-footer">
          <div className="modal-footer-left">
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={handleOpenInDesktop}
              disabled={isOpeningNative}
              title="Open the latest audit report file directly in your desktop markdown or text editor"
            >
              <ExternalLink size={13} className={isOpeningNative ? 'spin-anim' : ''} />
              <span>{isOpeningNative ? 'Opening...' : 'Open File'}</span>
            </button>
            {openNotice && (
              <span className={`open-notice-pill notice-${openNotice.type}`}>
                {openNotice.msg}
              </span>
            )}
          </div>
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}
