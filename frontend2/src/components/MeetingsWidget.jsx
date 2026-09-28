import React, { useState } from 'react';
import { Calendar, Clock, Video, Users, FileText, Plus, ExternalLink, CheckCircle } from 'lucide-react';

export default function MeetingsWidget({
  meetings = [],
  isProjectSpecific = false,
  project = null,
  onOpenNewMeetingModal,
  onSelectPrepDoc,
}) {
  const [filter, setFilter] = useState('all'); // 'all', 'today', 'upcoming'

  // Format date and time
  const formatMeetingTime = (isoString) => {
    const d = new Date(isoString);
    const timeStr = d.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
    const dateStr = d.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
    });
    return { timeStr, dateStr };
  };

  const getRelativeTimeBadge = (isoString) => {
    const diffMs = new Date(isoString).getTime() - new Date('2026-09-28T19:00:00').getTime();
    const diffHours = Math.round(diffMs / (1000 * 60 * 60));
    const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours > 0 && diffHours < 24) {
      return { label: `Tomorrow in ${diffHours}h`, cls: 'badge-soon' };
    }
    if (diffDays <= 1 && diffDays >= 0) {
      return { label: 'Tomorrow', cls: 'badge-soon' };
    }
    if (diffDays > 1 && diffDays <= 7) {
      return { label: `In ${diffDays} days`, cls: 'badge-upcoming' };
    }
    return { label: 'Upcoming', cls: 'badge-default' };
  };

  const filteredMeetings = meetings.filter((m) => {
    if (filter === 'today') {
      const d = new Date(m.startTime).getDate();
      return d === 28 || d === 29; // nearby
    }
    return true;
  });

  return (
    <div className="widget-card meetings-widget">
      <div className="widget-header">
        <div className="widget-title-group">
          <div className="widget-icon-wrapper meetings-accent">
            <Calendar size={18} />
          </div>
          <div>
            <h3 className="widget-title">
              {isProjectSpecific ? 'Project Meetings' : 'Upcoming Meetings'}
            </h3>
            <p className="widget-subtitle">
              {isProjectSpecific
                ? `Syncing calendar events for ${project?.code || 'this project'}`
                : 'Across all active workspaces & calendar feeds'}
            </p>
          </div>
        </div>

        <div className="widget-header-actions">
          <div className="tab-pills">
            <button
              className={`tab-pill ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All ({meetings.length})
            </button>
            <button
              className={`tab-pill ${filter === 'today' ? 'active' : ''}`}
              onClick={() => setFilter('today')}
            >
              Next 48h
            </button>
          </div>
          <button
            className="btn btn-secondary btn-icon-only"
            title="Schedule Meeting"
            onClick={onOpenNewMeetingModal}
          >
            <Plus size={16} />
          </button>
        </div>
      </div>

      <div className="widget-body">
        {filteredMeetings.length === 0 ? (
          <div className="widget-empty-state">
            <Calendar size={32} className="empty-icon" />
            <p>No upcoming meetings found</p>
            <button className="btn btn-outline btn-sm" onClick={onOpenNewMeetingModal}>
              Schedule a Meeting
            </button>
          </div>
        ) : (
          <div className="meetings-list">
            {filteredMeetings.map((meeting) => {
              const { timeStr, dateStr } = formatMeetingTime(meeting.startTime);
              const relativeBadge = getRelativeTimeBadge(meeting.startTime);

              return (
                <div key={meeting.id} className="meeting-item-card">
                  <div className="meeting-date-badge">
                    <span className="meeting-date-day">{dateStr.split(' ')[2]}</span>
                    <span className="meeting-date-month">{dateStr.split(' ')[1]}</span>
                  </div>

                  <div className="meeting-content">
                    <div className="meeting-top-row">
                      <span className={`time-badge ${relativeBadge.cls}`}>
                        <Clock size={12} />
                        {timeStr} • {relativeBadge.label}
                      </span>

                      {!isProjectSpecific && meeting.projectName && (
                        <span
                          className="project-pill-tag"
                          style={{
                            borderColor: meeting.projectColor || '#6366f1',
                            color: meeting.projectColor || '#818cf8',
                          }}
                        >
                          {meeting.projectName}
                        </span>
                      )}
                    </div>

                    <h4 className="meeting-name">{meeting.title}</h4>

                    {meeting.agenda && (
                      <p className="meeting-agenda-snippet">{meeting.agenda}</p>
                    )}

                    <div className="meeting-meta-row">
                      <div className="meeting-attendees">
                        <Users size={13} />
                        <span>{meeting.attendees?.length || 0} participants:</span>
                        <span className="attendee-names">
                          {meeting.attendees?.slice(0, 2).join(', ')}
                          {meeting.attendees?.length > 2 && ` +${meeting.attendees.length - 2}`}
                        </span>
                      </div>

                      {meeting.platform && (
                        <a
                          href={meeting.meetUrl || '#'}
                          target="_blank"
                          rel="noreferrer"
                          className="platform-link"
                          onClick={(e) => {
                            if (!meeting.meetUrl) e.preventDefault();
                          }}
                        >
                          <Video size={13} />
                          <span>{meeting.platform}</span>
                          <ExternalLink size={11} />
                        </a>
                      )}
                    </div>

                    {meeting.prepDoc && (
                      <div
                        className="meeting-prep-doc"
                        onClick={() => onSelectPrepDoc && onSelectPrepDoc(meeting.prepDoc)}
                        title="Click to inspect linked document/transcript"
                      >
                        <FileText size={13} />
                        <span>Context: <strong>{meeting.prepDoc}</strong></span>
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
