import React, { useState } from 'react';
import { X, Clock } from 'lucide-react';

export default function NewDeliverableModal({
  isOpen,
  onClose,
  projects = [],
  activeProject = null,
  onAddDeliverable,
}) {
  const [title, setTitle] = useState('');
  const [projectId, setProjectId] = useState(
    activeProject?.id || activeProject?.project_id || projects[0]?.id || projects[0]?.project_id || ''
  );
  const [dueDate, setDueDate] = useState('2026-10-06');
  const [priority, setPriority] = useState('high');
  const [owner, setOwner] = useState('Srinath');
  const [description, setDescription] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    const currentProjId = activeProject?.id || activeProject?.project_id || projectId;
    const selectedProj = projects.find((p) => (p.id || p.project_id) === currentProjId);

    const newDel = {
      id: `del_${Date.now()}`,
      title: title.trim(),
      projectId: selectedProj?.id || selectedProj?.project_id,
      projectName: selectedProj?.name,
      projectColor: selectedProj?.color,
      dueDate,
      status: 'in_progress',
      priority,
      progress: 10,
      owner: owner.trim() || 'Team',
      description: description.trim(),
    };

    onAddDeliverable(newDel);
    onClose();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <Clock size={20} className="modal-icon deliverables-accent" />
            <div>
              <h3 className="modal-title">Add Milestone Deliverable</h3>
              <span className="modal-subtitle">Track deadlines on the project timeline</span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label>Milestone / Deliverable Title *</label>
              <input
                type="text"
                required
                placeholder="e.g. Realtime WebSocket Notification Hub"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            {!activeProject && (
              <div className="form-group">
                <label>Associated Project</label>
                <select value={projectId} onChange={(e) => setProjectId(e.target.value)}>
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
                <label>Due Date</label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Priority</label>
                <select value={priority} onChange={(e) => setPriority(e.target.value)}>
                  <option value="high">High Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="low">Low Priority</option>
                </select>
              </div>

              <div className="form-group">
                <label>Owner</label>
                <input
                  type="text"
                  placeholder="Srinath"
                  value={owner}
                  onChange={(e) => setOwner(e.target.value)}
                />
              </div>
            </div>

            <div className="form-group">
              <label>Description & Acceptance Criteria</label>
              <textarea
                rows={3}
                placeholder="Key deliverables, testing benchmarks, and completion criteria..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Add Deliverable
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
