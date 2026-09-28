import React, { useState, useEffect } from 'react';
import { Layers, Activity, Calendar, Clock, Plus, FolderKanban } from 'lucide-react';
import { checkBackendHealth } from '../api';

export default function Navbar({ activeProject, onSelectProject, onOpenNewProjectModal }) {
  const [backendStatus, setBackendStatus] = useState({ online: false, checking: true });
  const [time, setTime] = useState('');

  useEffect(() => {
    async function verify() {
      const res = await checkBackendHealth();
      setBackendStatus({ online: res.online, checking: false });
    }
    verify();
    const interval = setInterval(verify, 15000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTime(
        now.toLocaleDateString('en-US', {
          weekday: 'short',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
        })
      );
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="navbar">
      <div className="navbar-left">
        <div className="brand" onClick={() => onSelectProject(null)}>
          <div className="brand-logo">
            <Layers className="brand-icon" size={20} />
          </div>
          <div className="brand-text">
            <span className="brand-title">Coordin8</span>
            <span className="brand-subtitle">Project & Knowledge Workspace</span>
          </div>
        </div>

        <div className="nav-breadcrumbs">
          <button
            className={`breadcrumb-item ${!activeProject ? 'active' : ''}`}
            onClick={() => onSelectProject(null)}
          >
            <FolderKanban size={15} />
            <span>Projects Overview</span>
          </button>
          {activeProject && (
            <>
              <span className="breadcrumb-separator">/</span>
              <div className="breadcrumb-item active project-crumb">
                <span
                  className="project-dot"
                  style={{ backgroundColor: activeProject.color }}
                />
                <span>{activeProject.name}</span>
                <span className="project-code-pill">{activeProject.code}</span>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="navbar-right">
        <div className="nav-time">
          <Clock size={14} />
          <span>{time}</span>
        </div>

        <div
          className={`backend-badge ${backendStatus.online ? 'online' : 'offline'}`}
          title={backendStatus.online ? 'FastAPI Backend online on port 8000' : 'Backend unreachable, using local storage'}
        >
          <span className="status-indicator-dot" />
          <span>{backendStatus.online ? 'Backend Live' : 'Local Mode'}</span>
        </div>

        {!activeProject && (
          <button className="btn btn-primary btn-sm" onClick={onOpenNewProjectModal}>
            <Plus size={15} />
            <span>New Project</span>
          </button>
        )}
      </div>
    </header>
  );
}
