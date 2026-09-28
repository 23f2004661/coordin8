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
} from 'lucide-react';
import FileExplorer from './FileExplorer';
import MeetingsWidget from './MeetingsWidget';
import DeliverablesWidget from './DeliverablesWidget';

export default function ProjectDetailView({
  project,
  backendDocs = [],
  onBack,
  onSelectDoc,
  onAddFileToProject,
  onRescanProject,
  onOpenNewMeetingModal,
  onOpenNewDeliverableModal,
  onToggleDeliverableStatus,
  onSelectPrepDoc,
}) {
  const [isRescanning, setIsRescanning] = useState(false);

  const totalFiles = (project.folders || []).reduce(
    (acc, f) => acc + (f.files ? f.files.length : 0),
    0
  );
  const projectMeetings = project.meetings || [];
  const projectDeliverables = project.deliverables || [];

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

  const folderPath =
    project.folder_path ||
    `C:\\Users\\ssrin\\Desktop\\Coordin8 Home\\${project.name}`;

  return (
    <div className="project-detail-layout">
      {/* Top Breadcrumb & Return Action */}
      <div className="project-detail-top-nav">
        <button className="btn btn-ghost btn-sm back-nav-btn" onClick={onBack}>
          <ArrowLeft size={16} />
          <span>Back to All Projects</span>
        </button>

        <div className="top-nav-right-actions">
          <div className="live-watcher-badge" title="Any file dropped into this folder in Windows Explorer is automatically indexed in real-time">
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

      {/* Project Hero Banner */}
      <div
        className="project-hero-banner"
        style={{ '--project-color': project.color || '#6366f1' }}
      >
        <div className="project-banner-main">
          <div className="project-banner-header-row">
            <div className="project-badge-group">
              <span className="project-code-tag">{project.code}</span>
              <span className="project-category-tag">{project.category}</span>
            </div>
            <div className="project-health-pill">
              <span>Overall Progress: <strong>{project.progress}%</strong></span>
            </div>
          </div>

          <h1 className="project-banner-title">{project.name}</h1>
          <p className="project-banner-desc">{project.description}</p>

          {/* Physical Directory Path on Disk */}
          <div className="project-physical-path-strip">
            <HardDrive size={14} className="path-icon" />
            <span className="path-label">Physical Directory:</span>
            <code className="path-code">{folderPath}</code>
          </div>

          <div className="project-banner-progress-track">
            <div
              className="project-banner-progress-fill"
              style={{
                width: `${project.progress}%`,
                backgroundColor: project.color || '#6366f1',
              }}
            />
          </div>
        </div>

        <div className="project-banner-stats">
          <div className="banner-stat-box">
            <FileText size={18} className="stat-icon" />
            <div className="stat-text-group">
              <span className="stat-value">{totalFiles}</span>
              <span className="stat-name">Indexed Files</span>
            </div>
          </div>
          <div className="banner-stat-box">
            <Calendar size={18} className="stat-icon" />
            <div className="stat-text-group">
              <span className="stat-value">{projectMeetings.length}</span>
              <span className="stat-name">Sync Meetings</span>
            </div>
          </div>
          <div className="banner-stat-box">
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

      {/* Main Split Layout: File Explorer (Left) & Project Specific Widgets (Right) */}
      <div className="project-split-layout">
        {/* Left Section: Files & Subfolders Explorer */}
        <div className="project-main-column">
          <div className="section-title-bar">
            <div className="title-left">
              <Layers size={18} className="column-icon" />
              <div>
                <h2 className="column-title">Project Files & Subfolders</h2>
                <p className="column-subtitle">
                  Browse physical folder contents, inspect indexed summaries, or drop files directly on disk.
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

        {/* Right Section: Project Specific Widgets (Meetings & Deliverables) */}
        <div className="project-sidebar-column">
          {/* Widget 1: Project-Specific Upcoming Meetings */}
          <MeetingsWidget
            meetings={projectMeetings}
            isProjectSpecific={true}
            project={project}
            onOpenNewMeetingModal={onOpenNewMeetingModal}
            onSelectPrepDoc={onSelectPrepDoc}
          />

          {/* Widget 2: Project-Specific Deliverables & Deadlines Timeline */}
          <DeliverablesWidget
            deliverables={projectDeliverables}
            isProjectSpecific={true}
            project={project}
            onOpenNewDeliverableModal={onOpenNewDeliverableModal}
            onToggleStatus={onToggleDeliverableStatus}
          />
        </div>
      </div>
    </div>
  );
}
