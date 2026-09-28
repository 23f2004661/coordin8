import React, { useState } from 'react';
import { CheckCircle2, Circle, Clock, AlertTriangle, Plus, Filter, User } from 'lucide-react';

export default function DeliverablesWidget({
  deliverables = [],
  isProjectSpecific = false,
  project = null,
  onOpenNewDeliverableModal,
  onToggleStatus,
}) {
  const [filter, setFilter] = useState('all'); // 'all', 'pending', 'completed'

  const getUrgencyBadge = (dueDate, status) => {
    if (status === 'completed') {
      return { label: 'Completed', cls: 'badge-completed' };
    }
    const dueTime = new Date(dueDate).getTime();
    const nowTime = new Date('2026-09-28T19:00:00').getTime();
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

  const filteredDeliverables = deliverables.filter((item) => {
    if (filter === 'pending') return item.status !== 'completed';
    if (filter === 'completed') return item.status === 'completed';
    return true;
  });

  return (
    <div className="widget-card deliverables-widget">
      <div className="widget-header">
        <div className="widget-title-group">
          <div className="widget-icon-wrapper deliverables-accent">
            <Clock size={18} />
          </div>
          <div>
            <h3 className="widget-title">
              {isProjectSpecific ? 'Project Deliverables' : 'Deliverables & Deadlines'}
            </h3>
            <p className="widget-subtitle">
              {isProjectSpecific
                ? `Milestone timeline for ${project?.code || 'this project'}`
                : 'Timeline & delivery tracking across all projects'}
            </p>
          </div>
        </div>

        <div className="widget-header-actions">
          <div className="tab-pills">
            <button
              className={`tab-pill ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All ({deliverables.length})
            </button>
            <button
              className={`tab-pill ${filter === 'pending' ? 'active' : ''}`}
              onClick={() => setFilter('pending')}
            >
              Active
            </button>
            <button
              className={`tab-pill ${filter === 'completed' ? 'active' : ''}`}
              onClick={() => setFilter('completed')}
            >
              Done
            </button>
          </div>
          <button
            className="btn btn-secondary btn-icon-only"
            title="Add Deliverable"
            onClick={onOpenNewDeliverableModal}
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      <div className="widget-body">
        {filteredDeliverables.length === 0 ? (
          <div className="widget-empty-state">
            <CheckCircle2 size={32} className="empty-icon" />
            <p>No deliverables match this filter</p>
            <button className="btn btn-outline btn-sm" onClick={onOpenNewDeliverableModal}>
              Create Deliverable
            </button>
          </div>
        ) : (
          <div className="timeline-container">
            <div className="timeline-track" />
            {filteredDeliverables.map((item) => {
              const urgency = getUrgencyBadge(item.dueDate, item.status);
              const isDone = item.status === 'completed';

              return (
                <div key={item.id} className={`timeline-node ${isDone ? 'is-completed' : ''}`}>
                  <button
                    className="timeline-status-btn"
                    onClick={() => onToggleStatus && onToggleStatus(item.id)}
                    title={isDone ? 'Mark as In Progress' : 'Mark as Completed'}
                  >
                    {isDone ? (
                      <CheckCircle2 size={20} className="status-icon done" />
                    ) : (
                      <Circle size={20} className="status-icon pending" />
                    )}
                  </button>

                  <div className="timeline-content-card">
                    <div className="timeline-top-row">
                      <span className={`time-badge ${urgency.cls}`}>
                        {urgency.label}
                      </span>

                      {!isProjectSpecific && item.projectName && (
                        <span
                          className="project-pill-tag"
                          style={{
                            borderColor: item.projectColor || '#6366f1',
                            color: item.projectColor || '#818cf8',
                          }}
                        >
                          {item.projectName}
                        </span>
                      )}

                      <span className={`priority-pill priority-${item.priority || 'medium'}`}>
                        {item.priority || 'medium'}
                      </span>
                    </div>

                    <h4 className={`timeline-title ${isDone ? 'strikethrough' : ''}`}>
                      {item.title}
                    </h4>

                    {item.description && (
                      <p className="timeline-desc">{item.description}</p>
                    )}

                    <div className="timeline-progress-section">
                      <div className="timeline-progress-bar-bg">
                        <div
                          className="timeline-progress-bar-fill"
                          style={{
                            width: `${isDone ? 100 : item.progress || 0}%`,
                            backgroundColor: isDone ? '#10b981' : item.projectColor || '#6366f1',
                          }}
                        />
                      </div>
                      <span className="timeline-progress-text">
                        {isDone ? 100 : item.progress || 0}%
                      </span>
                    </div>

                    {item.owner && (
                      <div className="timeline-owner-row">
                        <User size={12} />
                        <span>Owner: <strong>{item.owner}</strong></span>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
