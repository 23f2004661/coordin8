import React, { useState, useEffect } from 'react';
import { X, FolderPlus, Folder, HardDrive, Sparkles, AlertCircle } from 'lucide-react';
import { fetchHomeFolder } from '../api';

export default function NewProjectModal({ isOpen, onClose, onAddProject }) {
  const [creationMode, setCreationMode] = useState('scratch'); // 'scratch' or 'existing_folder'
  const [name, setName] = useState('');
  const [code, setCode] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('Core Infrastructure');
  const [color, setColor] = useState('#6366f1');
  const [folderPath, setFolderPath] = useState('');
  const [homeInfo, setHomeInfo] = useState({
    home_folder: 'C:\\Users\\ssrin\\Desktop\\Coordin8 Home',
    existing_folders: [],
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchHomeFolder().then((info) => {
        if (info) setHomeInfo(info);
      });
      setErrorMsg(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) return;

    if (creationMode === 'existing_folder' && !folderPath.trim()) {
      setErrorMsg('Please specify or select an existing folder path.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    const payload = {
      name: name.trim(),
      code: (code.trim() || name.substring(0, 3)).toUpperCase(),
      description: description.trim() || 'Project workspace with dedicated knowledge base.',
      category,
      color,
      creation_mode: creationMode,
      folder_path: creationMode === 'existing_folder' ? folderPath.trim() : null,
    };

    try {
      await onAddProject(payload);
      onClose();
    } catch (err) {
      setErrorMsg(err.message || 'Failed to create project');
    } finally {
      setIsSubmitting(false);
    }
  };

  const colors = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];
  const previewPath =
    creationMode === 'scratch'
      ? `${homeInfo.home_folder}\\${name.trim() || '<project-name>'}`
      : folderPath || 'Specify existing directory';

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-container project-create-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div className="modal-title-group">
            <FolderPlus size={20} className="modal-icon" />
            <div>
              <h3 className="modal-title">Create Project Workspace</h3>
              <span className="modal-subtitle">
                Isolated dedicated Knowledge Base with automatic file indexing
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {errorMsg && (
              <div className="form-alert-error">
                <AlertCircle size={15} />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Creation Mode Tabs */}
            <div className="mode-toggle-group">
              <button
                type="button"
                className={`mode-btn ${creationMode === 'scratch' ? 'active' : ''}`}
                onClick={() => setCreationMode('scratch')}
              >
                <Sparkles size={15} />
                <div className="mode-btn-text">
                  <span className="mode-title">Create from Scratch</span>
                  <span className="mode-desc">Creates new folder in Home Folder</span>
                </div>
              </button>

              <button
                type="button"
                className={`mode-btn ${creationMode === 'existing_folder' ? 'active' : ''}`}
                onClick={() => setCreationMode('existing_folder')}
              >
                <Folder size={15} />
                <div className="mode-btn-text">
                  <span className="mode-title">From Existing Folder</span>
                  <span className="mode-desc">Auto-index all files immediately</span>
                </div>
              </button>
            </div>

            {/* Home Folder Location Box */}
            <div className="home-folder-box">
              <HardDrive size={15} />
              <div className="home-folder-text">
                <span className="home-label">Configured Home Folder:</span>
                <code className="home-path">{homeInfo.home_folder}</code>
              </div>
            </div>

            {/* Project Name */}
            <div className="form-group">
              <label>Project Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Coordin8 Core Engine"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            {/* Existing Folder Selector (if mode is existing_folder) */}
            {creationMode === 'existing_folder' && (
              <div className="form-group">
                <label>Existing Folder Path *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. C:\Users\ssrin\Desktop\Coordin8 Home\my_project"
                  value={folderPath}
                  onChange={(e) => setFolderPath(e.target.value)}
                />
                {homeInfo.existing_folders && homeInfo.existing_folders.length > 0 && (
                  <div className="existing-folders-list">
                    <span className="existing-folders-label">Or choose from Home Folder:</span>
                    <div className="existing-chips">
                      {homeInfo.existing_folders.map((f) => (
                        <button
                          key={f.path}
                          type="button"
                          className="chip-btn"
                          onClick={() => {
                            setFolderPath(f.path);
                            if (!name) setName(f.name);
                          }}
                        >
                          <Folder size={12} />
                          <span>{f.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                <span className="field-hint">
                  All existing documents (.pdf, .docx, .xlsx, .md, .vtt, etc.) inside this directory will be automatically ingested into this project's dedicated vector store.
                </span>
              </div>
            )}

            {/* Target Path Preview */}
            <div className="target-path-preview">
              <span className="preview-label">Physical Directory on Disk:</span>
              <code className="preview-path">{previewPath}</code>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Project Code</label>
                <input
                  type="text"
                  placeholder="e.g. CORE-RAG"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Category</label>
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option value="Core Infrastructure">Core Infrastructure</option>
                  <option value="Agent Orchestration">Agent Orchestration</option>
                  <option value="User Experience">User Experience</option>
                  <option value="Research & Evals">Research & Evals</option>
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>Description</label>
              <textarea
                rows={2}
                placeholder="Objectives and scope for this project workspace..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label>Theme Accent Color</label>
              <div className="color-picker-row">
                {colors.map((c) => (
                  <button
                    key={c}
                    type="button"
                    className={`color-swatch ${color === c ? 'selected' : ''}`}
                    style={{ backgroundColor: c }}
                    onClick={() => setColor(c)}
                  />
                ))}
              </div>
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Initializing KnowledgeBase...' : 'Create Project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
