import React, { useState } from 'react';
import {
  ArrowLeft,
  Folder,
  FileText,
  Calendar,
  Clock,
  Plus,
  Layers,
  HardDrive,
  RefreshCw,
  Eye,
  CheckCircle2,
  Circle,
  Building2,
  Briefcase,
  Sparkles,
  AlertCircle,
  Mail,
  Edit3,
  Check,
  X,
  Trash2,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  FileSpreadsheet,
  Link2,
  Copy,
} from 'lucide-react';
import FileExplorer from './FileExplorer';
import MeetingsWidget from './MeetingsWidget';
import UploadTranscriptModal from './UploadTranscriptModal';
import AuditReportModal from './AuditReportModal';
import { openFileInNativeApp, openProjectFolderInNativeOS, breakdownDeliverable } from '../api';

export default function ProjectDetailView({
  project,
  projects = [],
  backendDocs = [],
  allEmails = [],
  onBack,
  onSelectDoc,
  onAddFileToProject,
  onRescanProject,
  onOpenNewMeetingModal,
  onOpenNewDeliverableModal,
  onOpenGoogleCalendarModal,
  onAssignMeetingsToProject,
  gcalSession = null,
  onToggleDeliverableStatus,
  onSelectPrepDoc,
  onTranscriptUploaded,
  onUpdateProject,
  onAnalyzeDeliverables,
  onAcceptDiscoveredDeliverable,
  onDismissDiscoveredDeliverable,
  onDeleteDeliverable,
  onAssignEmailToProject,
}) {
  const [activeTab, setActiveTab] = useState('timeline'); // 'timeline', 'files', 'context'
  const [isRescanning, setIsRescanning] = useState(false);
  const [isAuditingAI, setIsAuditingAI] = useState(false);
  const [auditError, setAuditError] = useState(null);
  const [isAuditModalOpen, setIsAuditModalOpen] = useState(false);
  const [auditSuccessBanner, setAuditSuccessBanner] = useState(null);
  const [openingFile, setOpeningFile] = useState(null);
  const [breakingDownId, setBreakingDownId] = useState(null);

  const handleBreakdown = async (deliverableId) => {
    setBreakingDownId(deliverableId);
    try {
      await breakdownDeliverable(project.id || project.project_id, deliverableId);
      if (onRescanProject) {
        await onRescanProject(project.id || project.project_id);
      }
    } catch (err) {
      console.error('Task breakdown error:', err);
      alert(`AI Task Breakdown failed: ${err.message}`);
    } finally {
      setBreakingDownId(null);
    }
  };

  const handleOpenFileByName = async (fileName) => {
    setOpeningFile(fileName);
    try {
      await openFileInNativeApp({
        projectId: project.id || project.project_id,
        fileName,
      });
    } catch (err) {
      console.error('Failed to open file:', err);
      alert(`Could not open ${fileName}: ${err.message}`);
    } finally {
      setOpeningFile(null);
    }
  };

  const handleOpenFolder = async () => {
    try {
      await openProjectFolderInNativeOS(project.id || project.project_id);
    } catch (err) {
      console.error('Failed to open folder:', err);
      alert(`Could not open project folder: ${err.message}`);
    }
  };

  // In-line editing of Problem Statement & Client Info
  const [isEditingContext, setIsEditingContext] = useState(false);
  const [editProblemStatement, setEditProblemStatement] = useState(
    project.problem_statement || project.description || ''
  );
  const [editClientName, setEditClientName] = useState(project.client_name || '');
  const [editClientEmail, setEditClientEmail] = useState(project.client_email || '');
  const [editProjectType, setEditProjectType] = useState(project.project_type || 'internal');

  // Filter for deliverables
  const [deliverableFilter, setDeliverableFilter] = useState('all');

  // Meeting transcript modal
  const [selectedMeetingForTranscript, setSelectedMeetingForTranscript] = useState(null);

  const totalFiles = (project.folders || []).reduce(
    (acc, f) => acc + (f.files ? f.files.length : 0),
    0
  );
  const projectMeetings = project.meetings || [];
  const projectDeliverables = project.deliverables || [];
  const discoveredDeliverables = project.discovered_deliverables || [];
  const aiAnalysis = project.ai_analysis || null;

  // Filter project-specific emails
  const projectEmails = (allEmails || []).filter(
    (e) => e.projectId === (project.id || project.project_id)
  );

  const handleRescan = async () => {
    setIsRescanning(true);
    try {
      if (onRescanProject) {
        await onRescanProject(project.id || project.project_id);
      }
    } finally {
      setTimeout(() => setIsRescanning(false), 600);
    }
  };

  const handleRunAIAudit = async () => {
    setIsAuditingAI(true);
    setAuditError(null);
    setAuditSuccessBanner(null);
    try {
      if (onAnalyzeDeliverables) {
        const res = await onAnalyzeDeliverables(project.id || project.project_id);
        const rPath =
          res?.analysis?.latestReportPath ||
          res?.analysis?.reportFile ||
          `${folderPath}\\audit_reports\\latest_audit_report.md`;
        setAuditSuccessBanner({
          message: 'AI Deliverable Audit Complete! Evidence verified across documents & communications.',
          reportPath: rPath,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        });
        // Automatically open the full audit report modal to reveal evidence and exact report file
        setIsAuditModalOpen(true);
      }
    } catch (err) {
      setAuditError(err.message || 'AI deliverable analysis failed');
    } finally {
      setIsAuditingAI(false);
    }
  };

  const handleSaveContext = async () => {
    if (onUpdateProject) {
      await onUpdateProject(project.id || project.project_id, {
        problem_statement: editProblemStatement.trim(),
        project_type: editProjectType,
        client_name: editProjectType === 'client' ? editClientName.trim() : '',
        client_email: editProjectType === 'client' ? editClientEmail.trim() : '',
      });
    }
    setIsEditingContext(false);
  };

  const folderPath =
    project.folder_path ||
    `C:\\Users\\ssrin\\Desktop\\Coordin8 Home\\${project.name}`;

  const latestReportPath =
    aiAnalysis?.latestReportPath ||
    aiAnalysis?.reportFile ||
    `${folderPath}\\audit_reports\\latest_audit_report.md`;

  const getUrgencyBadge = (dueDate, status) => {
    if (status === 'completed') {
      return { label: 'Completed', cls: 'badge-completed' };
    }
    const dueTime = new Date(dueDate).getTime();
    const nowTime = Date.now();
    const diffDays = Math.round((dueTime - nowTime) / (1000 * 60 * 60 * 24));

    if (diffDays < 0) {
      return { label: `${Math.abs(diffDays)}d Overdue`, cls: 'badge-urgent' };
    }
    if (diffDays === 0) {
      return { label: 'Due Today', cls: 'badge-urgent' };
    }
    if (diffDays <= 2) {
      return { label: `Due in ${diffDays}d`, cls: 'badge-soon' };
    }
    if (diffDays <= 7) {
      return { label: `Due in ${diffDays}d`, cls: 'badge-upcoming' };
    }
    return { label: `Due ${dueDate}`, cls: 'badge-default' };
  };

  const filteredDeliverables = projectDeliverables.filter((item) => {
    if (deliverableFilter === 'pending') return item.status !== 'completed';
    if (deliverableFilter === 'completed') return item.status === 'completed';
    return true;
  });

  return (
    <div className="project-detail-layout">
      {/* Top Breadcrumb & Return Action */}
      <div className="project-detail-top-nav">
        <button className="btn btn-ghost btn-sm back-nav-btn" onClick={onBack}>
          <ArrowLeft size={16} />
          <span>Back to All Projects</span>
        </button>

        <div className="top-nav-right-actions">
          <div
            className="live-watcher-badge"
            title="Any file dropped into this folder in Windows Explorer is automatically indexed in real-time"
          >
            <span className="live-pulse-dot" />
            <span>Auto-Indexing Watcher Active</span>
          </div>

          <button
            className="btn btn-secondary btn-sm"
            onClick={handleRescan}
            disabled={isRescanning}
            title="Scan project folder for any newly added files"
          >
            <RefreshCw size={13} className={isRescanning ? 'spin-anim' : ''} />
            <span>{isRescanning ? 'Scanning...' : 'Rescan Folder'}</span>
          </button>
        </div>
      </div>

      {/* Project Hero Banner & Strategic Context */}
      <div
        className="project-hero-banner"
        style={{ '--project-color': project.color || '#6366f1' }}
      >
        <div className="project-banner-main">
          <div className="project-banner-header-row">
            <div className="project-badge-group">
              <span className="project-code-tag">{project.code}</span>
              <span className="project-category-tag">{project.category}</span>
              <span className={`project-type-tag ${project.project_type === 'client' ? 'type-client' : 'type-internal'}`}>
                {project.project_type === 'client' ? (
                  <>
                    <Building2 size={12} />
                    <span>Client: {project.client_name || 'External Client'}</span>
                  </>
                ) : (
                  <>
                    <Briefcase size={12} />
                    <span>Internal Project</span>
                  </>
                )}
              </span>
            </div>

            <div className="project-health-pill">
              <span>Overall Progress: <strong>{project.progress || 0}%</strong></span>
              {aiAnalysis?.health && (
                <span className={`health-status-badge health-${aiAnalysis.health}`}>
                  {aiAnalysis.health === 'on_track' ? 'On Track' : aiAnalysis.health === 'at_risk' ? 'At Risk' : 'Delayed'}
                </span>
              )}
            </div>
          </div>

          <h1 className="project-banner-title">{project.name}</h1>

          {/* Problem Statement & Background Context Block */}
          <div className="problem-statement-card">
            <div className="problem-statement-header">
              <div className="problem-header-left">
                <span className="context-label">Main Problem Statement & Background Context</span>
              </div>
              {!isEditingContext ? (
                <button
                  type="button"
                  className="btn btn-ghost btn-xs edit-context-btn"
                  onClick={() => {
                    setEditProblemStatement(project.problem_statement || project.description || '');
                    setEditClientName(project.client_name || '');
                    setEditClientEmail(project.client_email || '');
                    setEditProjectType(project.project_type || 'internal');
                    setIsEditingContext(true);
                  }}
                >
                  <Edit3 size={13} />
                  <span>Edit Context</span>
                </button>
              ) : (
                <div className="edit-context-actions">
                  <button type="button" className="btn btn-primary btn-xs" onClick={handleSaveContext}>
                    <Check size={13} />
                    <span>Save</span>
                  </button>
                  <button type="button" className="btn btn-ghost btn-xs" onClick={() => setIsEditingContext(false)}>
                    <X size={13} />
                    <span>Cancel</span>
                  </button>
                </div>
              )}
            </div>

            {!isEditingContext ? (
              <p className="problem-statement-text">
                {project.problem_statement || project.description || 'No problem statement defined yet. Click "Edit Context" to describe the background and work going on in this project.'}
              </p>
            ) : (
              <div className="problem-statement-edit-form">
                <div className="edit-form-row">
                  <div className="edit-field">
                    <label>Project Type</label>
                    <select
                      value={editProjectType}
                      onChange={(e) => setEditProjectType(e.target.value)}
                    >
                      <option value="internal">Internal Initiative</option>
                      <option value="client">Client-Specific Project</option>
                    </select>
                  </div>
                  {editProjectType === 'client' && (
                    <>
                      <div className="edit-field">
                        <label>Client Name</label>
                        <input
                          type="text"
                          value={editClientName}
                          placeholder="e.g. Acme Corp"
                          onChange={(e) => setEditClientName(e.target.value)}
                        />
                      </div>
                      <div className="edit-field">
                        <label>Client Email</label>
                        <input
                          type="email"
                          value={editClientEmail}
                          placeholder="client@acme.com"
                          onChange={(e) => setEditClientEmail(e.target.value)}
                        />
                      </div>
                    </>
                  )}
                </div>

                <div className="edit-field">
                  <label>Problem Statement & Objectives</label>
                  <textarea
                    rows={3}
                    value={editProblemStatement}
                    placeholder="Describe the background context and ongoing work..."
                    onChange={(e) => setEditProblemStatement(e.target.value)}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Project Quick Actions */}
          <div className="project-quick-actions-bar">
            <button
              type="button"
              className="btn btn-ghost btn-xs open-explorer-btn"
              onClick={handleOpenFolder}
              title="Open project folder in Windows File Explorer"
            >
              <Folder size={13} />
              <span>Open Folder in Explorer</span>
            </button>
          </div>

          <div className="project-banner-progress-track">
            <div
              className="project-banner-progress-fill"
              style={{
                width: `${project.progress || 0}%`,
                backgroundColor: project.color || '#6366f1',
              }}
            />
          </div>
        </div>

        <div className="project-banner-stats">
          <div className="banner-stat-box" onClick={() => setActiveTab('files')}>
            <FileText size={18} className="stat-icon" />
            <div className="stat-text-group">
              <span className="stat-value">{totalFiles}</span>
              <span className="stat-name">Indexed Files</span>
            </div>
          </div>
          <div className="banner-stat-box" onClick={() => setActiveTab('context')}>
            <Calendar size={18} className="stat-icon" />
            <div className="stat-text-group">
              <span className="stat-value">{projectMeetings.length}</span>
              <span className="stat-name">Sync Meetings</span>
            </div>
          </div>
          <div className="banner-stat-box" onClick={() => setActiveTab('context')}>
            <Mail size={18} className="stat-icon" />
            <div className="stat-text-group">
              <span className="stat-value">{projectEmails.length}</span>
              <span className="stat-name">Client Emails</span>
            </div>
          </div>
          <div className="banner-stat-box" onClick={() => setActiveTab('timeline')}>
            <Clock size={18} className="stat-icon" />
            <div className="stat-text-group">
              <span className="stat-value">
                {projectDeliverables.filter((d) => d.status !== 'completed').length}
              </span>
              <span className="stat-name">Open Milestones</span>
            </div>
          </div>
        </div>
      </div>

      {/* Project Navigation View Tabs */}
      <div className="project-view-tabs-bar">
        <button
          className={`project-tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          <Clock size={16} />
          <span>Timeline & Deliverables</span>
          <span className="tab-counter-pill">{projectDeliverables.length}</span>
        </button>

        <button
          className={`project-tab-btn ${activeTab === 'files' ? 'active' : ''}`}
          onClick={() => setActiveTab('files')}
        >
          <Layers size={16} />
          <span>Project Files & Evidence</span>
          <span className="tab-counter-pill">{totalFiles}</span>
        </button>

        <button
          className={`project-tab-btn ${activeTab === 'context' ? 'active' : ''}`}
          onClick={() => setActiveTab('context')}
        >
          <Mail size={16} />
          <span>Ambient Context & Inputs</span>
          <span className="tab-counter-pill">{projectEmails.length + projectMeetings.length}</span>
        </button>
      </div>

      {/* Tab 1: Timeline & Deliverables (Primary High-Leverage Outcomes View) */}
      {activeTab === 'timeline' && (
        <div className="timeline-view-layout">
          {/* AI Progress Intelligence Banner */}
          <div className="ai-intelligence-panel">
            <div className="ai-intel-header">
              <div className="ai-intel-title-group">
                <div className="ai-sparkle-circle">
                  <Sparkles size={18} />
                </div>
                <div>
                  <h3 className="ai-intel-title">Autonomous Deliverable & Progress Intelligence</h3>
                  <p className="ai-intel-subtitle">
                    Cross-references problem statement with Excel spreadsheets, PDFs, meeting transcripts, and emails.
                  </p>
                </div>
              </div>

              <div className="ai-intel-actions-row">
                {aiAnalysis && (
                  <>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm open-audit-app-btn"
                      onClick={() => handleOpenFileByName('latest_audit_report.md')}
                      disabled={openingFile === 'latest_audit_report.md'}
                      title="Open latest_audit_report.md directly in your desktop application (Notepad, VS Code, Word, etc.)"
                    >
                      <ExternalLink size={14} className={openingFile === 'latest_audit_report.md' ? 'spin-anim' : ''} />
                      <span>{openingFile === 'latest_audit_report.md' ? 'Opening...' : 'Open Audit Report'}</span>
                    </button>

                    <button
                      type="button"
                      className="btn btn-outline btn-sm view-audit-report-btn"
                      onClick={() => setIsAuditModalOpen(true)}
                      title="Open full evidence-anchored markdown audit briefing"
                    >
                      <FileText size={14} />
                      <span>View Briefing</span>
                    </button>
                  </>
                )}

                <button
                  type="button"
                  className="btn btn-primary btn-sm ai-audit-btn"
                  onClick={handleRunAIAudit}
                  disabled={isAuditingAI}
                >
                  <Sparkles size={14} className={isAuditingAI ? 'spin-anim' : ''} />
                  <span>{isAuditingAI ? 'Auditing Artifacts & Progress...' : 'Audit Progress with AI'}</span>
                </button>
              </div>
            </div>

            {/* Success Toast / Notification */}
            {auditSuccessBanner && (
              <div className="audit-success-toast">
                <CheckCircle2 size={16} className="toast-success-icon" />
                <div className="toast-text-group">
                  <span className="toast-title">{auditSuccessBanner.message}</span>
                </div>
                <button
                  type="button"
                  className="btn btn-secondary btn-xs"
                  onClick={() => handleOpenFileByName('latest_audit_report.md')}
                >
                  <ExternalLink size={12} />
                  <span>Open File</span>
                </button>
                <button
                  type="button"
                  className="btn btn-primary btn-xs"
                  onClick={() => setIsAuditModalOpen(true)}
                >
                  View Briefing
                </button>
                <button
                  type="button"
                  className="btn btn-ghost btn-xs"
                  onClick={() => setAuditSuccessBanner(null)}
                >
                  <X size={13} />
                </button>
              </div>
            )}

            {auditError && (
              <div className="form-alert-error" style={{ marginTop: '0.75rem' }}>
                <AlertCircle size={15} />
                <span>{auditError}</span>
              </div>
            )}

            {aiAnalysis ? (
              <div className="ai-intel-body">
                <div className="ai-intel-briefing">
                  <span className="briefing-tag">Executive Status Briefing:</span>
                  <p className="briefing-text">{aiAnalysis.executiveSummary}</p>
                </div>

                <div className="ai-intel-metrics">
                  <div className="ai-metric-item">
                    <span className="ai-metric-label">Estimated Completion</span>
                    <span className="ai-metric-val">{aiAnalysis.overallCompletion}%</span>
                  </div>
                  <div className="ai-metric-item">
                    <span className="ai-metric-label">Project Health</span>
                    <span className={`ai-metric-val health-text-${aiAnalysis.health}`}>
                      {aiAnalysis.health === 'on_track' ? '● On Track' : aiAnalysis.health === 'at_risk' ? '▲ At Risk' : '✕ Delayed'}
                    </span>
                  </div>
                  <div className="ai-metric-item">
                    <span className="ai-metric-label">Last Audited</span>
                    <span className="ai-metric-val sub">
                      {new Date(aiAnalysis.lastAnalyzedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="ai-intel-placeholder">
                <span>Click <strong>"Audit Progress with AI"</strong> to evaluate deliverables against project documents and client communications.</span>
              </div>
            )}
          </div>

          {/* AI Discovered Deliverables Queue (Ambient Ingestion Pillar 1) */}
          {discoveredDeliverables.length > 0 && (
            <div className="discovered-queue-section">
              <div className="discovered-queue-header">
                <Sparkles size={16} className="sparkle-amber" />
                <h4>Discovered Milestones from Communications & Specs ({discoveredDeliverables.length})</h4>
                <span className="discovered-badge-hint">Review AI-extracted commitments before adding to timeline</span>
              </div>

              <div className="discovered-cards-grid">
                {discoveredDeliverables.map((item, idx) => (
                  <div key={idx} className="discovered-card">
                    <div className="discovered-card-top">
                      <span className={`priority-pill priority-${item.priority || 'medium'}`}>
                        {item.priority || 'medium'}
                      </span>
                      <span className="source-citation-badge">
                        From {item.source || 'Communication'}
                      </span>
                    </div>

                    <h5 className="discovered-card-title">{item.title}</h5>
                    <p className="discovered-card-desc">{item.description}</p>

                    {item.sourceEvidence && (
                      <div className="discovered-evidence-snippet">
                        <Link2 size={12} />
                        <span>{item.sourceEvidence}</span>
                      </div>
                    )}

                    <div className="discovered-card-actions">
                      <button
                        type="button"
                        className="btn btn-primary btn-xs"
                        onClick={() => onAcceptDiscoveredDeliverable && onAcceptDiscoveredDeliverable(project.id || project.project_id, item)}
                      >
                        <Plus size={12} />
                        <span>Accept to Timeline</span>
                      </button>

                      <button
                        type="button"
                        className="btn btn-ghost btn-xs"
                        onClick={() => onDismissDiscoveredDeliverable && onDismissDiscoveredDeliverable(project.id || project.project_id, item.title)}
                      >
                        <X size={12} />
                        <span>Dismiss</span>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Main Deliverables Timeline Container */}
          <div className="project-timeline-wrapper">
            <div className="timeline-header-bar">
              <div className="timeline-header-left">
                <Clock size={18} className="deliverables-accent" />
                <div>
                  <h3 className="section-title">Milestone Roadmap & Timeline</h3>
                  <p className="section-subtitle">
                    Evidence-anchored deliverables tracked against canonical project documents
                  </p>
                </div>
              </div>

              <div className="timeline-header-actions">
                <div className="tab-pills">
                  <button
                    className={`tab-pill ${deliverableFilter === 'all' ? 'active' : ''}`}
                    onClick={() => setDeliverableFilter('all')}
                  >
                    All ({projectDeliverables.length})
                  </button>
                  <button
                    className={`tab-pill ${deliverableFilter === 'pending' ? 'active' : ''}`}
                    onClick={() => setDeliverableFilter('pending')}
                  >
                    In Progress
                  </button>
                  <button
                    className={`tab-pill ${deliverableFilter === 'completed' ? 'active' : ''}`}
                    onClick={() => setDeliverableFilter('completed')}
                  >
                    Completed
                  </button>
                </div>

                <button
                  type="button"
                  className="btn btn-primary btn-sm"
                  onClick={onOpenNewDeliverableModal}
                >
                  <Plus size={15} />
                  <span>Add Deliverable</span>
                </button>
              </div>
            </div>

            {filteredDeliverables.length === 0 ? (
              <div className="widget-empty-state">
                <CheckCircle2 size={36} className="empty-icon" />
                <p>No deliverables match this filter.</p>
                <button className="btn btn-outline btn-sm" onClick={onOpenNewDeliverableModal}>
                  Create First Deliverable
                </button>
              </div>
            ) : (
              <div className="timeline-container full-timeline">
                <div className="timeline-track" />
                {filteredDeliverables.map((item) => {
                  const urgency = getUrgencyBadge(item.dueDate, item.status);
                  const isDone = item.status === 'completed';
                  const audit = item.aiAudit;

                  return (
                    <div key={item.id} className={`timeline-node ${isDone ? 'is-completed' : ''}`}>
                      <button
                        type="button"
                        className="timeline-status-btn"
                        onClick={() => onToggleDeliverableStatus && onToggleDeliverableStatus(item.id)}
                        title={isDone ? 'Mark as In Progress' : 'Mark as Completed'}
                      >
                        {isDone ? (
                          <CheckCircle2 size={22} className="status-icon done" />
                        ) : (
                          <Circle size={22} className="status-icon pending" />
                        )}
                      </button>

                      <div className="timeline-content-card rich-node">
                        <div className="timeline-top-row">
                          <span className={`time-badge ${urgency.cls}`}>
                            {urgency.label}
                          </span>

                          <span className={`priority-pill priority-${item.priority || 'medium'}`}>
                            {item.priority || 'medium'}
                          </span>

                          {item.source && (
                            <span className="source-pill">
                              {item.source === 'email' ? 'From Email' : item.source === 'meeting_transcript' ? 'From Meeting' : item.source === 'document' ? 'From Spec / SOW' : 'Manual'}
                            </span>
                          )}

                          <button
                            type="button"
                            className="btn btn-ghost btn-icon-only btn-xs delete-deliverable-btn"
                            title="Delete Deliverable"
                            onClick={() => onDeleteDeliverable && onDeleteDeliverable(project.id || project.project_id, item.id)}
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>

                        <h4 className={`timeline-title ${isDone ? 'strikethrough' : ''}`}>
                          {item.title}
                        </h4>

                        {item.description && (
                          <p className="timeline-desc">{item.description}</p>
                        )}

                        {/* Progress Bar */}
                        <div className="timeline-progress-section">
                          <div className="timeline-progress-bar-bg">
                            <div
                              className="timeline-progress-bar-fill"
                              style={{
                                width: `${isDone ? 100 : item.progress || 0}%`,
                                backgroundColor: isDone ? '#10b981' : project.color || '#6366f1',
                              }}
                            />
                          </div>
                          <span className="timeline-progress-text">
                            {isDone ? 100 : item.progress || 0}%
                          </span>
                        </div>

                        {/* AI Evidence Anchoring */}
                        {audit && audit.evidence && (
                          <div className="deliverable-evidence-panel">
                            <div className="evidence-header">
                              <Sparkles size={12} className="sparkle-icon" />
                              <span>AI Proof-of-Work Verification</span>
                            </div>
                            <p className="evidence-text">{audit.evidence}</p>
                            {audit.evidenceFiles && audit.evidenceFiles.length > 0 && (
                              <div className="evidence-files-list">
                                {audit.evidenceFiles.map((fn, fIdx) => (
                                  <button
                                    key={fIdx}
                                    type="button"
                                    className="evidence-file-chip clickable"
                                    onClick={() => handleOpenFileByName(fn)}
                                    title={`Click to open ${fn} in its native desktop application (Excel, Word, PDF Reader, etc.)`}
                                  >
                                    <FileSpreadsheet size={11} />
                                    <span>{fn}</span>
                                    <ExternalLink size={10} className="open-ext-icon" />
                                  </button>
                                ))}
                              </div>
                            )}
                            {audit.blockers && (
                              <div className="evidence-blocker-note">
                                <AlertCircle size={11} />
                                <span>Remaining Blocker: {audit.blockers}</span>
                              </div>
                            )}
                          </div>
                        )}
                        {/* AI Decomposed Execution Tasks */}
                        <div className="deliverable-tasks-section">
                          <div className="tasks-section-header">
                            <div className="tasks-header-left">
                              <Layers size={13} className="sparkle-icon" />
                              <span className="tasks-header-title">Operational Execution Tasks ({item.tasks ? item.tasks.length : 0})</span>
                            </div>
                            {(!item.tasks || item.tasks.length === 0) && (
                              <button
                                type="button"
                                className="btn btn-outline btn-xs breakdown-btn"
                                disabled={breakingDownId === item.id}
                                onClick={() => handleBreakdown(item.id)}
                              >
                                <Sparkles size={11} />
                                <span>{breakingDownId === item.id ? 'Generating Tasks...' : 'AI Task Breakdown'}</span>
                              </button>
                            )}
                          </div>

                          {item.tasks && item.tasks.length > 0 && (
                            <div className="tasks-sublist">
                              {item.tasks.map((task) => (
                                <div key={task.id} className={`task-subcard ${task.status === 'completed' ? 'task-done' : ''}`}>
                                  <div className="task-subcard-header">
                                    <span className="task-title-text">{task.title}</span>
                                    <span className={`task-stage-badge stage-${task.stage || 'draft'}`}>
                                      {(task.stage || 'draft').replace('_', ' ').toUpperCase()}
                                    </span>
                                  </div>
                                  <p className="task-desc-text">{task.description}</p>
                                  <div className="task-footer-row">
                                    <span className="task-target-artifact">
                                      <FileText size={11} />
                                      <span>{task.targetArtifact}</span>
                                    </span>
                                    <span className="task-meta-assignee">
                                      {task.assignedTo || 'Specialist'} ({task.estimatedHours || 8}h)
                                    </span>
                                    <span className={`task-status-pill status-${task.status || 'todo'}`}>
                                      {task.status === 'completed' ? 'Completed' : task.status === 'in_progress' ? 'In Progress' : 'To Do'}
                                    </span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>

                        <div className="timeline-bottom-meta">
                          {item.owner && (
                            <span className="timeline-meta-owner">
                              Owner: <strong>{item.owner}</strong>
                            </span>
                          )}
                          {item.sourceEvidence && (
                            <span className="timeline-meta-evidence">
                              <Link2 size={11} />
                              <span>{item.sourceEvidence}</span>
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Project Files & Evidence Explorer */}
      {activeTab === 'files' && (
        <div className="project-files-layout">
          <div className="section-title-bar">
            <div className="title-left">
              <Layers size={18} className="column-icon" />
              <div>
                <h2 className="column-title">Project Files & Multimodal Knowledge</h2>
                <p className="column-subtitle">
                  Inspect indexed spreadsheets, PDF specs, presentations, and transcripts powering AI deliverable evaluation.
                </p>
              </div>
            </div>
          </div>

          <FileExplorer
            project={project}
            backendDocs={backendDocs}
            onSelectDoc={onSelectDoc}
            onAddFileToProject={onAddFileToProject}
          />
        </div>
      )}

      {/* Tab 3: Ambient Context & Inputs (Client Emails & Meeting Transcripts) */}
      {activeTab === 'context' && (
        <div className="project-context-stream-layout">
          <div className="context-split-columns">
            {/* Left: Client Communications & Emails Feed */}
            <div className="context-column emails-column">
              <div className="context-column-header">
                <div className="context-header-left">
                  <Mail size={18} className="context-icon mail-accent" />
                  <div>
                    <h3 className="context-column-title">Client Communications (Gmail)</h3>
                    <p className="context-column-sub">
                      Ambient email context categorized into intent archetypes & action capsules.
                    </p>
                  </div>
                </div>
              </div>

              {projectEmails.length === 0 ? (
                <div className="widget-empty-state">
                  <Mail size={32} className="empty-icon" />
                  <p>No emails currently matched to this project.</p>
                  <span className="empty-sub">
                    Emails mentioning project code "{project.code}" or sender "{project.client_email || project.client_name || 'client'}" are matched automatically.
                  </span>
                </div>
              ) : (
                <div className="email-cards-stream">
                  {projectEmails.map((email) => (
                    <div key={email.id} className="email-context-card">
                      <div className="email-card-header">
                        <div className="email-sender-info">
                          <span className="email-sender-name">{email.senderName || email.from}</span>
                          <span className="email-date">
                            {new Date(email.receivedAt).toLocaleDateString([], { month: 'short', day: 'numeric' })}
                          </span>
                        </div>

                        {/* Standardized Archetype Badge */}
                        <div className="archetype-badge-group">
                          {email.archetype && (
                            <span className="archetype-pill">
                              {email.archetype}
                            </span>
                          )}
                          {email.actionTag && (
                            <span className="action-tag-pill">
                              {email.actionTag}
                            </span>
                          )}
                        </div>
                      </div>

                      <h4 className="email-subject">{email.subject}</h4>
                      <p className="email-snippet">{email.snippet}</p>

                      {email.aiSummary && (
                        <div className="email-ai-summary">
                          <Sparkles size={11} />
                          <span>{email.aiSummary}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right: Scheduled Meetings & Transcripts */}
            <div className="context-column meetings-column">
              <MeetingsWidget
                meetings={projectMeetings}
                projects={projects}
                isProjectSpecific={true}
                project={project}
                onOpenNewMeetingModal={onOpenNewMeetingModal}
                onOpenGoogleCalendarModal={onOpenGoogleCalendarModal}
                onAssignMeetingsToProject={onAssignMeetingsToProject}
                gcalSession={gcalSession}
                onSelectPrepDoc={onSelectPrepDoc}
                onTranscriptUploaded={onTranscriptUploaded}
              />
            </div>
          </div>
        </div>
      )}

      {/* AI Deliverable Audit Report Modal */}
      <AuditReportModal
        isOpen={isAuditModalOpen}
        onClose={() => setIsAuditModalOpen(false)}
        project={project}
        onAcceptCandidate={(candidate) =>
          onAcceptDiscoveredDeliverable &&
          onAcceptDiscoveredDeliverable(project.id || project.project_id, candidate)
        }
      />
    </div>
  );
}
