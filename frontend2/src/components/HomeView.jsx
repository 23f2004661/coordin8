import React from 'react';
import { FolderKanban, Plus, Calendar, Clock, Sparkles } from 'lucide-react';
import ProjectCard from './ProjectCard';
import MeetingsWidget from './MeetingsWidget';
import DeliverablesWidget from './DeliverablesWidget';

export default function HomeView({
  projects = [],
  allMeetings = [],
  allDeliverables = [],
  onSelectProject,
  onOpenNewProjectModal,
  onOpenNewMeetingModal,
  onOpenNewDeliverableModal,
  onToggleDeliverableStatus,
  onSelectPrepDoc,
}) {
  return (
    <div className="home-view-layout">
      {/* Hero / Header Section */}
      <section className="home-hero-section">
        <div className="hero-text-content">
          <div className="hero-pill">
            <Sparkles size={14} className="sparkle-icon" />
            <span>Autonomous Project Management & Multimodal RAG</span>
          </div>
          <h1 className="hero-heading">Welcome to your Workspaces</h1>
          <p className="hero-description">
            Organize documents, track project meetings across your Google Calendar feeds, and monitor deliverable deadlines in one centralized command center.
          </p>
        </div>

        <div className="hero-metrics-strip">
          <div className="metric-box">
            <span className="metric-number">{projects.length}</span>
            <span className="metric-label">Active Projects</span>
          </div>
          <div className="metric-divider" />
          <div className="metric-box">
            <span className="metric-number">{allMeetings.length}</span>
            <span className="metric-label">Upcoming Meetings</span>
          </div>
          <div className="metric-divider" />
          <div className="metric-box">
            <span className="metric-number">
              {allDeliverables.filter((d) => d.status !== 'completed').length}
            </span>
            <span className="metric-label">Open Milestones</span>
          </div>
        </div>
      </section>

      {/* Projects Window / Folders Section */}
      <section className="projects-window-section">
        <div className="section-header">
          <div className="section-title-group">
            <div className="section-icon-box">
              <FolderKanban size={18} />
            </div>
            <div>
              <h2 className="section-title">My Projects</h2>
              <div className="home-folder-indicator">
                <span>Home Folder:</span>
                <code>C:\Users\ssrin\Desktop\Coordin8 Home</code>
              </div>
            </div>
          </div>

          <button className="btn btn-primary btn-sm" onClick={onOpenNewProjectModal}>
            <Plus size={15} />
            <span>Create Project</span>
          </button>
        </div>

        <div className="projects-grid">
          {projects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onSelectProject={onSelectProject}
            />
          ))}

          {/* Quick Create Card */}
          <div className="project-create-placeholder-card" onClick={onOpenNewProjectModal}>
            <div className="create-icon-circle">
              <Plus size={24} />
            </div>
            <span className="create-card-title">Add Another Project</span>
            <span className="create-card-sub">Create folder & initialize isolated vector space</span>
          </div>
        </div>
      </section>

      {/* Global Widgets Section (Upcoming Meetings + Deliverables Timeline) */}
      <section className="global-widgets-section">
        <div className="widgets-grid-layout">
          {/* Widget 1: Upcoming Meetings Across All Projects */}
          <div className="widget-column">
            <MeetingsWidget
              meetings={allMeetings}
              isProjectSpecific={false}
              onOpenNewMeetingModal={onOpenNewMeetingModal}
              onSelectPrepDoc={onSelectPrepDoc}
            />
          </div>

          {/* Widget 2: Deliverables & Deadlines Timeline Across All Projects */}
          <div className="widget-column">
            <DeliverablesWidget
              deliverables={allDeliverables}
              isProjectSpecific={false}
              onOpenNewDeliverableModal={onOpenNewDeliverableModal}
              onToggleStatus={onToggleDeliverableStatus}
            />
          </div>
        </div>
      </section>
    </div>
  );
}
