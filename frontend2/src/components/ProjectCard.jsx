import React from 'react';
import { Folder, FileText, Calendar, Clock, ArrowRight, Building2, Briefcase } from 'lucide-react';

export default function ProjectCard({ project, onSelectProject }) {
  // Count total files across subfolders
  const totalFiles = (project.folders || []).reduce(
    (acc, f) => acc + (f.files ? f.files.length : 0),
    0
  );
  const meetingsCount = (project.meetings || []).length;
  const activeDeliverables = (project.deliverables || []).filter(
    (d) => d.status !== 'completed'
  ).length;

  const isClient = project.project_type === 'client';
  const problemStatement = project.problem_statement || project.description || '';

  return (
    <div
      className="project-folder-card"
      onClick={() => onSelectProject(project)}
      style={{ '--card-accent': project.color || '#0066cc' }}
    >
      <div className="project-card-top">
        <div className="project-folder-icon-box" style={{ backgroundColor: `${project.color || '#0066cc'}18` }}>
          <Folder size={20} style={{ color: project.color || '#0066cc' }} />
        </div>
        <div className="project-card-meta">
          <span className="project-code">{project.code}</span>
          {isClient ? (
            <span className="project-type-chip client-chip" title={`Client: ${project.client_name || 'External'}`}>
              <Building2 size={11} />
              <span>{project.client_name || 'Client'}</span>
            </span>
          ) : (
            <span className="project-type-chip internal-chip">
              <Briefcase size={11} />
              <span>Internal</span>
            </span>
          )}
          <span className="project-category-pill">{project.category}</span>
        </div>
      </div>

      <div className="project-card-info">
        <h3 className="project-name">{project.name}</h3>
        <p className="project-desc">{problemStatement}</p>
      </div>

      <div className="project-progress-container">
        <div className="project-progress-header">
          <span>Overall Health</span>
          <span className="progress-percent">{project.progress || 0}%</span>
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-indicator"
            style={{
              width: `${project.progress || 0}%`,
              backgroundColor: project.color || '#6366f1',
            }}
          />
        </div>
      </div>

      <div className="project-card-footer">
        <div className="project-stat-pill" title={`${totalFiles} files registered`}>
          <FileText size={14} />
          <span>{totalFiles} files</span>
        </div>
        <div className="project-stat-pill" title={`${meetingsCount} meetings scheduled`}>
          <Calendar size={14} />
          <span>{meetingsCount} syncs</span>
        </div>
        <div className="project-stat-pill" title={`${activeDeliverables} active milestones`}>
          <Clock size={14} />
          <span>{activeDeliverables} tasks</span>
        </div>
        <button className="project-enter-btn" aria-label="Open project">
          <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}
