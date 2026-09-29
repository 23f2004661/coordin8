import React, { useState, useRef } from 'react';
import {
  X,
  FileText,
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  Folder,
  Layers,
  Sparkles,
  ArrowRight,
} from 'lucide-react';
import { uploadMeetingTranscript } from '../api';

export default function UploadTranscriptModal({
  isOpen,
  onClose,
  meeting,
  projects = [],
  onUploadSuccess,
}) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [assignMode, setAssignMode] = useState(
    meeting?.projectId ? 'project' : 'general' // 'project' or 'general'
  );
  const [targetProjectId, setTargetProjectId] = useState(
    meeting?.projectId || projects[0]?.id || projects[0]?.project_id || ''
  );
  const [isUploading, setIsUploading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const fileInputRef = useRef(null);

  if (!isOpen || !meeting) return null;

  const currentProject = projects.find(
    (p) => (p.id || p.project_id) === (meeting.projectId || targetProjectId)
  );

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  };

  const handleFileSelected = (file) => {
    setErrorMsg('');
    const validExtensions = ['.txt', '.vtt', '.docx', '.pdf', '.md'];
    const name = file.name.toLowerCase();
    const isValid = validExtensions.some((ext) => name.endsWith(ext));
    if (!isValid) {
      setErrorMsg('Please upload a supported text, transcript, or document file (.txt, .vtt, .docx, .pdf, .md).');
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMsg('Please select a transcript file to upload.');
      return;
    }

    const meetingId = meeting.id || meeting.gcalId;
    const finalProjectId = assignMode === 'project' ? targetProjectId : 'general';

    try {
      setIsUploading(true);
      setErrorMsg('');
      const result = await uploadMeetingTranscript(meetingId, selectedFile, finalProjectId);
      if (onUploadSuccess) {
        onUploadSuccess(result);
      }
      onClose();
    } catch (err) {
      console.error('Failed to upload transcript:', err);
      setErrorMsg(err.message || 'Failed to upload and index transcript.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-container upload-transcript-modal">
        {/* Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <div className="modal-icon-badge accent-purple">
              <UploadCloud size={20} />
            </div>
            <div>
              <h3 className="modal-title">Upload Meeting Transcript</h3>
              <p className="modal-subtitle">
                Feed ambient meeting context into Coordin8's RAG and deliverable intelligence
              </p>
            </div>
          </div>
          <button type="button" className="btn-icon modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Meeting context banner */}
        <div className="meeting-context-banner">
          <div className="context-banner-info">
            <span className="context-label">Completed Meeting</span>
            <h4 className="context-title">{meeting.title}</h4>
            <span className="context-time">
              {new Date(meeting.startTime).toLocaleString(undefined, {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
              })}
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="transcript-modal-body">
          {/* Project assignment prompt */}
          <div className="form-section">
            <label className="section-label">Knowledge Base Destination</label>

            {!meeting.projectId ? (
              <div className="assignment-choice-group">
                <div className="assignment-prompt-box">
                  <AlertCircle size={16} className="text-warning" />
                  <span>
                    This meeting is currently <strong>unassigned</strong>. Choose whether to link it to a specific project or keep it general:
                  </span>
                </div>

                <div className="choice-cards-row">
                  <div
                    className={`choice-card ${assignMode === 'project' ? 'is-selected' : ''}`}
                    onClick={() => setAssignMode('project')}
                  >
                    <div className="choice-card-header">
                      <input
                        type="radio"
                        name="assignMode"
                        checked={assignMode === 'project'}
                        onChange={() => setAssignMode('project')}
                      />
                      <Folder size={16} className="choice-icon text-indigo" />
                      <span className="choice-title">Assign to Project</span>
                    </div>
                    <p className="choice-description">
                      Indexed directly into the project's dedicated vector space and saved in its physical transcripts folder.
                    </p>

                    {assignMode === 'project' && (
                      <div className="choice-project-select-wrapper" onClick={(e) => e.stopPropagation()}>
                        <select
                          className="input-select"
                          value={targetProjectId}
                          onChange={(e) => setTargetProjectId(e.target.value)}
                        >
                          {projects.map((p) => (
                            <option key={p.id || p.project_id} value={p.id || p.project_id}>
                              {p.name}
                            </option>
                          ))}
                        </select>
                      </div>
                    )}
                  </div>

                  <div
                    className={`choice-card ${assignMode === 'general' ? 'is-selected' : ''}`}
                    onClick={() => setAssignMode('general')}
                  >
                    <div className="choice-card-header">
                      <input
                        type="radio"
                        name="assignMode"
                        checked={assignMode === 'general'}
                        onChange={() => setAssignMode('general')}
                      />
                      <Layers size={16} className="choice-icon text-cyan" />
                      <span className="choice-title">Leave Unassigned / Multi-Project</span>
                    </div>
                    <p className="choice-description">
                      Indexed into workspace <code>general</code> folder. Best for company-wide standups, 1-on-1s, or cross-project status reviews.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="assigned-destination-badge">
                <span
                  className="project-dot"
                  style={{ backgroundColor: currentProject?.color || meeting.projectColor || '#6366f1' }}
                />
                <span>
                  Indexing into: <strong>{currentProject?.name || meeting.projectName}</strong> Knowledge Base
                </span>
              </div>
            )}
          </div>

          {/* File Dropzone */}
          <div className="form-section">
            <label className="section-label">Select Transcript File</label>
            <div
              className={`transcript-dropzone ${dragActive ? 'is-drag-active' : ''} ${
                selectedFile ? 'has-file' : ''
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="hidden-file-input"
                accept=".txt,.vtt,.docx,.pdf,.md"
                onChange={handleFileChange}
              />

              {selectedFile ? (
                <div className="selected-file-preview">
                  <div className="file-badge-icon">
                    <FileText size={24} />
                  </div>
                  <div className="file-info-col">
                    <span className="file-name">{selectedFile.name}</span>
                    <span className="file-size">
                      {(selectedFile.size / 1024).toFixed(1)} KB • Click to replace
                    </span>
                  </div>
                  <CheckCircle2 size={18} className="text-success check-icon" />
                </div>
              ) : (
                <div className="dropzone-empty-content">
                  <UploadCloud size={28} className="dropzone-icon" />
                  <p className="dropzone-text">
                    Drag & drop transcript here, or <span>Browse files</span>
                  </p>
                  <span className="dropzone-sub">Supports .txt, .vtt, .docx, .pdf, .md</span>
                </div>
              )}
            </div>
          </div>

          {errorMsg && (
            <div className="form-error-banner">
              <AlertCircle size={15} />
              <span>{errorMsg}</span>
            </div>
          )}

          {/* Action Footer */}
          <div className="modal-actions-row">
            <button
              type="button"
              className="btn btn-ghost"
              onClick={onClose}
              disabled={isUploading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!selectedFile || isUploading}
            >
              {isUploading ? (
                <>
                  <Sparkles size={15} className="spin-icon" />
                  <span>Indexing Transcript into Vector DB...</span>
                </>
              ) : (
                <>
                  <UploadCloud size={15} />
                  <span>Upload & Index Transcript</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
