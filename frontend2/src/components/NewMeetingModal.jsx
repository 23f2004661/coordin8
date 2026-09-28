import React, { useState } from 'react';
import { X, Calendar } from 'lucide-react';

export default function NewMeetingModal({
  isOpen,
  onClose,
  projects = [],
  activeProject = null,
  onAddMeeting,
}) {
  const [title, setTitle] = useState('');
  const [projectId, setProjectId] = useState(activeProject?.id || projects[0]?.id || '');
  const [date, setDate] = useState('2026-09-30');
  const [time, setTime] = useState('11:00');
  const [duration, setDuration] = useState('45 min');
  const [attendees, setAttendees] = useState('Srinath, Priya');
  const [meetUrl, setMeetUrl] = useState('https://meet.google.com/new-sync');
  const [agenda, setAgenda] = useState('');
  const [prepDoc, setPrepDoc] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const selectedProj = projects.find((p) => p.id === (activeProject?.id || projectId));
    const startIso = `${date}T${time}:00`;

    const newMeeting = {
      id: `m_${Date.now()}`,
      title: title.trim(),
      projectId: selectedProj?.id,
      projectName: selectedProj?.name,
      projectColor: selectedProj?.color,
      startTime: startIso,
      endTime: startIso,
      duration,
      platform: 'Google Meet',
      meetUrl: meetUrl.trim(),
      attendees: attendees.split(',').map((s) => s.trim()).filter(Boolean),
      agenda: agenda.trim(),
      prepDoc: prepDoc.trim(),
      status: 'confirmed',
    };

    onAddMeeting(newMeeting);
    onClose();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <Calendar size={20} className="modal-icon meetings-accent" />
            <div>
              <h3 className="modal-title">Schedule Project Meeting</h3>
              <span className="modal-subtitle">Connect calendar sync & link prep documents</span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Meeting Title *</label>
              <input
                type="text"
                required
                placeholder="e.g. Sprint Architecture Sync"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            {!activeProject && (
              <div className="form-group">
                <label>Associated Project</label>
                <select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
                  {projects.map((p) => (
                    <option key={p.id} value={p.id}>
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
                  placeholder="30 min"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Attendees (comma separated)</label>
              <input
                type="text"
                placeholder="Srinath, Priya, Alex"
                value={attendees}
                onChange={(e) => setAttendees(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Google Meet URL</label>
              <input
                type="url"
                placeholder="https://meet.google.com/..."
                value={meetUrl}
                onChange={(e) => setMeetUrl(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Agenda / Discussion Topics</label>
              <textarea
                rows={2}
                placeholder="Main points to cover in this session..."
                value={agenda}
                onChange={(e) => setAgenda(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Linked Context / Prep Document</label>
              <input
                type="text"
                placeholder="e.g. ProjectDetails.md or Architecture_Review_Q3.vtt"
                value={prepDoc}
                onChange={(e) => setPrepDoc(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Schedule Event
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
