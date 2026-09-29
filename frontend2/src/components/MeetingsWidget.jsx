import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Video,
  Users,
  FileText,
  Plus,
  ExternalLink,
  CheckCircle,
  CheckSquare,
  Square,
  ArrowRight,
  UploadCloud,
} from 'lucide-react';
import { cleanAgendaText } from '../services/googleCalendar';
import UploadTranscriptModal from './UploadTranscriptModal';

export default function MeetingsWidget({
  meetings = [],
  projects = [],
  isProjectSpecific = false,
  project = null,
  onOpenNewMeetingModal,
  onOpenGoogleCalendarModal,
  onAssignMeetingsToProject,
  gcalSession = null,
  onSelectPrepDoc,
  onTranscriptUploaded,
}) {
  const [filter, setFilter] = useState('all'); // 'all', 'today', 'upcoming'
  const [selectedMeetingIds, setSelectedMeetingIds] = useState([]);
  const [batchTargetProjectId, setBatchTargetProjectId] = useState(
    projects[0]?.id || projects[0]?.project_id || ''
  );

  // Live dynamic clock updated every 30 seconds
  const [currentTime, setCurrentTime] = useState(new Date());
  const [uploadTranscriptMeeting, setUploadTranscriptMeeting] = useState(null);

  const isMeetingCompleted = (m) => {
    if (m.status === 'completed') return true;
    const meetingEnd = m.endTime
      ? new Date(m.endTime).getTime()
      : new Date(m.startTime).getTime() + (m.durationMinutes || 30) * 60000;
    return meetingEnd < currentTime.getTime();
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 30000);
    return () => clearInterval(timer);
  }, []);

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
    const target = new Date(isoString);
    const now = currentTime;
    const diffMs = target.getTime() - now.getTime();
    const diffMinutes = Math.round(diffMs / (1000 * 60));
    const diffHours = Math.round(diffMs / (1000 * 60 * 60));

    // Calendar day comparison based on local midnight
    const midnightNow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const midnightTarget = new Date(target.getFullYear(), target.getMonth(), target.getDate());
    const calendarDayDiff = Math.round(
      (midnightTarget.getTime() - midnightNow.getTime()) / (1000 * 60 * 60 * 24)
    );

    // Meeting is Today
    if (calendarDayDiff === 0) {
      if (diffMinutes < -60) {
        return { label: 'Earlier today', cls: 'badge-default' };
      }
      if (diffMinutes >= -60 && diffMinutes < 0) {
        return { label: 'Happening now', cls: 'badge-soon' };
      }
      if (diffMinutes >= 0 && diffMinutes <= 1) {
        return { label: 'Starting now', cls: 'badge-soon' };
      }
      if (diffMinutes > 1 && diffMinutes < 60) {
        return { label: `Today in ${diffMinutes}m`, cls: 'badge-soon' };
      }
      return { label: `Today in ${diffHours}h`, cls: 'badge-soon' };
    }

    // Meeting is Tomorrow
    if (calendarDayDiff === 1) {
      if (diffHours <= 24 && diffHours > 0) {
        return { label: `Tomorrow in ${diffHours}h`, cls: 'badge-soon' };
      }
      return { label: 'Tomorrow', cls: 'badge-soon' };
    }

    // Meeting is Yesterday or in the Past
    if (calendarDayDiff < 0) {
      if (calendarDayDiff === -1) {
        return { label: 'Yesterday', cls: 'badge-default' };
      }
      return { label: 'Past', cls: 'badge-default' };
    }

    // Upcoming within 7 days
    if (calendarDayDiff <= 7) {
      return { label: `In ${calendarDayDiff} days`, cls: 'badge-upcoming' };
    }

    return { label: 'Upcoming', cls: 'badge-default' };
  };

  const filteredMeetings = meetings.filter((m) => {
    if (filter === 'today') {
      const mTime = new Date(m.startTime).getTime();
      const nowTime = currentTime.getTime();
      // Within next 48 hours and not ended more than 1 hour ago
      return mTime >= nowTime - 60 * 60 * 1000 && mTime <= nowTime + 48 * 60 * 60 * 1000;
    }
    return true;
  });

  const handleToggleSelect = (id) => {
    setSelectedMeetingIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const visibleIds = filteredMeetings.map((m) => m.id || m.gcalId);
  const isAllSelected =
    visibleIds.length > 0 && visibleIds.every((id) => selectedMeetingIds.includes(id));

  const handleToggleSelectAll = () => {
    if (isAllSelected) {
      setSelectedMeetingIds((prev) => prev.filter((id) => !visibleIds.includes(id)));
    } else {
      setSelectedMeetingIds((prev) => Array.from(new Set([...prev, ...visibleIds])));
    }
  };

  const handleBatchApply = () => {
    if (selectedMeetingIds.length === 0) return;
    if (onAssignMeetingsToProject) {
      onAssignMeetingsToProject(selectedMeetingIds, batchTargetProjectId);
      setSelectedMeetingIds([]);
    }
  };

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
          <button
            className={`btn-google-sync ${gcalSession?.connected ? 'connected' : ''}`}
            onClick={onOpenGoogleCalendarModal}
            title={
              gcalSession?.connected
                ? `Connected: ${gcalSession.user?.email || 'Google Account'}. Click to manage sync.`
                : 'Connect your Google Calendar to sync meetings'
            }
          >
            <Calendar size={13} style={{ color: gcalSession?.connected ? '#34d399' : '#4285f4' }} />
            <span>{gcalSession?.connected ? 'Google Synced' : 'Sync Google Calendar'}</span>
            {gcalSession?.connected && <span className="live-pulse-dot" style={{ width: '5px', height: '5px' }} />}
          </button>

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
        {/* Batch Project Assignment Bar */}
        {selectedMeetingIds.length > 0 && projects.length > 0 && onAssignMeetingsToProject && (
          <div className="widget-batch-bar">
            <div className="batch-bar-left">
              <button
                type="button"
                className="select-all-btn"
                onClick={handleToggleSelectAll}
              >
                {isAllSelected ? (
                  <CheckSquare size={16} className="check-icon-active" />
                ) : (
                  <Square size={16} />
                )}
                <span>{selectedMeetingIds.length} meeting(s) selected</span>
              </button>
            </div>

            <div className="batch-action-controls">
              <span className="batch-label">Assign to:</span>
              <select
                value={batchTargetProjectId}
                onChange={(e) => setBatchTargetProjectId(e.target.value)}
                className="batch-project-select"
              >
                <option value="">Unassigned (No Project)</option>
                {projects.map((p) => (
                  <option key={p.id || p.project_id} value={p.id || p.project_id}>
                    {p.name}
                  </option>
                ))}
              </select>

              <button
                type="button"
                className="btn btn-primary btn-sm batch-apply-btn"
                onClick={handleBatchApply}
              >
                <ArrowRight size={13} />
                <span>Assign ({selectedMeetingIds.length})</span>
              </button>

              <button
                type="button"
                className="btn btn-ghost btn-sm"
                onClick={() => setSelectedMeetingIds([])}
              >
                Cancel
              </button>
            </div>
          </div>
        )}

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
              const mId = meeting.id || meeting.gcalId;
              const isSelected = selectedMeetingIds.includes(mId);
              const { timeStr, dateStr } = formatMeetingTime(meeting.startTime);
              const relativeBadge = getRelativeTimeBadge(meeting.startTime);
              const currentProj = projects.find(
                (p) => (p.id || p.project_id) === meeting.projectId
              );

              return (
                <div
                  key={mId}
                  className={`meeting-item-card ${isSelected ? 'is-selected' : ''}`}
                >
                  <div className="widget-meeting-left-group">
                    {/* Checkbox button */}
                    <button
                      type="button"
                      className={`widget-checkbox-btn ${isSelected ? 'checked' : ''}`}
                      onClick={() => handleToggleSelect(mId)}
                      title={isSelected ? 'Deselect meeting' : 'Select meeting for project assignment'}
                    >
                      {isSelected ? (
                        <CheckSquare size={17} className="check-icon-active" />
                      ) : (
                        <Square size={17} />
                      )}
                    </button>

                    <div className="meeting-date-badge">
                      <span className="meeting-date-day">{dateStr.split(' ')[2]}</span>
                      <span className="meeting-date-month">{dateStr.split(' ')[1]}</span>
                    </div>
                  </div>

                  <div className="meeting-content">
                    <div className="meeting-top-row">
                      <span className={`time-badge ${relativeBadge.cls}`}>
                        <Clock size={12} />
                        {timeStr} • {relativeBadge.label}
                      </span>

                      {/* Interactive project selector or tag */}
                      {!isProjectSpecific && onAssignMeetingsToProject ? (
                        <div
                          className="widget-project-badge-dropdown"
                          title="Click to reassign meeting to another project or leave unassigned"
                        >
                          <span
                            className="project-dot"
                            style={{
                              backgroundColor: meeting.projectId
                                ? (currentProj?.color || meeting.projectColor || '#6366f1')
                                : '#94a3b8',
                            }}
                          />
                          <select
                            value={meeting.projectId || ''}
                            onChange={(e) => {
                              onAssignMeetingsToProject([mId], e.target.value);
                            }}
                            className="widget-project-inline-select"
                          >
                            <option value="">Unassigned</option>
                            {projects.map((p) => (
                              <option key={p.id || p.project_id} value={p.id || p.project_id}>
                                {p.name}
                              </option>
                            ))}
                          </select>
                        </div>
                      ) : (
                        !isProjectSpecific && (
                          <span
                            className="project-pill-tag"
                            style={{
                              borderColor: meeting.projectId ? (meeting.projectColor || '#6366f1') : '#94a3b8',
                              color: meeting.projectId ? (meeting.projectColor || '#818cf8') : '#64748b',
                            }}
                          >
                            {meeting.projectName || 'Unassigned'}
                          </span>
                        )
                      )}

                      {meeting.isGcal && (
                        <span className="gcal-source-badge" title="Synchronized from Google Calendar">
                          <Calendar size={11} />
                          <span>Google Calendar</span>
                        </span>
                      )}
                    </div>

                    <h4 className="meeting-name">{meeting.title}</h4>

                    {cleanAgendaText(meeting.agenda) && (
                      <p className="meeting-agenda-snippet">{cleanAgendaText(meeting.agenda)}</p>
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

                    {meeting.prepDoc && !meeting.hasTranscript && (
                      <div
                        className="meeting-prep-doc"
                        onClick={() => onSelectPrepDoc && onSelectPrepDoc(meeting.prepDoc)}
                        title="Click to inspect linked document/transcript"
                      >
                        <FileText size={13} />
                        <span>Context: <strong>{meeting.prepDoc}</strong></span>
                      </div>
                    )}

                    {/* Completed Meeting Transcript Action */}
                    {isMeetingCompleted(meeting) && (
                      <div className="meeting-transcript-section">
                        {meeting.transcriptFile || (meeting.prepDoc && meeting.hasTranscript) ? (
                          <div
                            className="meeting-transcript-pill"
                            onClick={() => {
                              if (onSelectPrepDoc) onSelectPrepDoc(meeting.transcriptFile || meeting.prepDoc);
                              else setUploadTranscriptMeeting(meeting);
                            }}
                            title="Transcript indexed into knowledge base. Click to view or replace."
                          >
                            <FileText size={13} className="text-success" />
                            <span className="transcript-name">
                              Transcript: <strong>{meeting.transcriptFile || meeting.prepDoc}</strong>
                            </span>
                            <button
                              type="button"
                              className="btn-replace-transcript"
                              onClick={(e) => {
                                e.stopPropagation();
                                setUploadTranscriptMeeting(meeting);
                              }}
                              title="Replace transcript file"
                            >
                              Replace
                            </button>
                          </div>
                        ) : (
                          <button
                            type="button"
                            className="btn btn-sm btn-upload-transcript"
                            onClick={() => setUploadTranscriptMeeting(meeting)}
                            title="Upload transcript or notes for this completed meeting"
                          >
                            <UploadCloud size={13} />
                            <span>Upload Transcript</span>
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {uploadTranscriptMeeting && (
        <UploadTranscriptModal
          isOpen={Boolean(uploadTranscriptMeeting)}
          onClose={() => setUploadTranscriptMeeting(null)}
          meeting={uploadTranscriptMeeting}
          projects={projects}
          onUploadSuccess={(result) => {
            if (onTranscriptUploaded) {
              onTranscriptUploaded(result);
            }
            setUploadTranscriptMeeting(null);
          }}
        />
      )}
    </div>
  );
}
