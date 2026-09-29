import React, { useState, useEffect } from 'react';
import { X, Calendar, Video, Loader2, AlertCircle } from 'lucide-react';
import { createGoogleCalendarEvent, getSavedSession } from '../services/googleCalendar';

export default function NewMeetingModal({
  isOpen,
  onClose,
  projects = [],
  activeProject = null,
  onAddMeeting,
  gcalSession = null,
  setGcalSession = null,
}) {
  const getTodayDate = () => {
    const d = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
  };

  const getUpcomingTime = () => {
    const d = new Date();
    d.setHours(d.getHours() + 1, 0, 0, 0);
    const pad = (n) => String(n).padStart(2, '0');
    return `${pad(d.getHours())}:${pad(d.getMinutes())}`;
  };

  const [title, setTitle] = useState('');
  const [projectId, setProjectId] = useState(
    activeProject?.id || activeProject?.project_id || ''
  );
  const [date, setDate] = useState(getTodayDate());
  const [time, setTime] = useState(getUpcomingTime());
  const [duration, setDuration] = useState('30 min');
  const [attendees, setAttendees] = useState('');
  const [agenda, setAgenda] = useState('');
  const [prepDoc, setPrepDoc] = useState('');

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (isOpen) {
      setProjectId(activeProject?.id || activeProject?.project_id || '');
      setTitle('');
      setDate(getTodayDate());
      setTime(getUpcomingTime());
      setDuration('30 min');
      setAttendees('');
      setAgenda('');
      setPrepDoc('');
      setErrorMessage('');
      setIsSubmitting(false);
    }
  }, [isOpen, activeProject]);

  if (!isOpen) return null;

  const currentSession = gcalSession || getSavedSession();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    setErrorMessage('');

    const currentProjId = activeProject?.id || activeProject?.project_id || projectId;
    const selectedProj = projects.find((p) => (p.id || p.project_id) === currentProjId) || null;

    try {
      // Call Google Calendar API to create event + Google Meet
      const { meeting, session: newSession } = await createGoogleCalendarEvent({
        title: title.trim(),
        date,
        time,
        duration,
        attendees,
        agenda: agenda.trim(),
        prepDoc: prepDoc.trim(),
        targetProject: selectedProj,
        allProjects: projects,
      });

      if (newSession && setGcalSession) {
        setGcalSession(newSession);
      }

      onAddMeeting(meeting);
      onClose();
    } catch (err) {
      console.error('Error creating Google Calendar meeting:', err);
      setErrorMessage(
        err.message || 'Failed to create Google Calendar event and Google Meet link.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <Calendar size={20} className="modal-icon meetings-accent" />
            <div>
              <h3 className="modal-title">Schedule Project Meeting</h3>
              <span className="modal-subtitle">Auto-generate Google Meet & sync to calendar</span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} disabled={isSubmitting}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {errorMessage && (
              <div className="modal-error-banner">
                <AlertCircle size={16} />
                <div className="error-banner-content">
                  <span>{errorMessage}</span>
                </div>
              </div>
            )}

            {/* Google Meet Auto-Creation Indicator */}
            <div className="gmeet-auto-card">
              <div className="gmeet-auto-header">
                <div className="gmeet-badge-icon">
                  <Video size={16} />
                </div>
                <div className="gmeet-auto-info">
                  <div className="gmeet-auto-title">Google Meet Integration</div>
                  <div className="gmeet-auto-sub">
                    A new Google Meet link will be automatically generated and added to this event.
                  </div>
                </div>
              </div>

              {currentSession?.connected ? (
                <div className="gmeet-account-status connected">
                  <span className="live-pulse-dot" />
                  <span>Google Account: <strong>{currentSession.user?.email}</strong></span>
                </div>
              ) : (
                <div className="gmeet-account-status prompt">
                  <span>You will be prompted to authorize your Google Account when scheduling.</span>
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Meeting Title *</label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            {!activeProject && (
              <div className="form-group">
                <label>Associated Project</label>
                <select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
                  <option value="">Unassigned (No Project)</option>
                  {projects.map((p) => (
                    <option key={p.id || p.project_id} value={p.id || p.project_id}>
                      {p.name} ({p.code})
                    </option>
                  ))}
                </select>
              </div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label>Date</label>
                <input
                  type="date"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Time</label>
                <input
                  type="time"
                  value={time}
                  onChange={(e) => setTime(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Duration</label>
                <input
                  type="text"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Attendee Emails (comma-separated)</label>
              <input
                type="text"
                value={attendees}
                onChange={(e) => setAttendees(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Agenda / Discussion Topics</label>
              <textarea
                rows={2}
                value={agenda}
                onChange={(e) => setAgenda(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Linked Context / Prep Document</label>
              <input
                type="text"
                value={prepDoc}
                onChange={(e) => setPrepDoc(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary btn-submit-meeting"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 size={15} className="spinner-icon" />
                  <span>Creating Google Meet...</span>
                </>
              ) : (
                <>
                  <Video size={15} />
                  <span>Schedule & Create Meet</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
