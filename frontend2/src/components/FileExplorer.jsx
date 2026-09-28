import React, { useState, useRef } from 'react';
import {
  Folder,
  FolderOpen,
  FileText,
  FileCode,
  FileSpreadsheet,
  FileAudio,
  File,
  Upload,
  Search,
  Plus,
  ArrowLeft,
  Eye,
  CheckCircle2,
  Clock,
  HardDrive,
  ExternalLink,
} from 'lucide-react';
import { uploadDocumentToBackend } from '../api';

export default function FileExplorer({
  project,
  backendDocs = [],
  onSelectDoc,
  onAddFileToProject,
}) {
  const [selectedFolderId, setSelectedFolderId] = useState(null); // null = all folders
  const [searchQuery, setSearchQuery] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [activeTab, setActiveTab] = useState('project'); // 'project' or 'backend'
  const fileInputRef = useRef(null);

  const folders = project.folders || [];
  const activeFolder = folders.find((f) => f.id === selectedFolderId);

  // Collect files based on selection
  let displayedFiles = [];
  if (selectedFolderId && activeFolder) {
    displayedFiles = activeFolder.files || [];
  } else {
    // Flatten all files from all folders
    folders.forEach((f) => {
      (f.files || []).forEach((file) => {
        displayedFiles.push({ ...file, folderName: f.name });
      });
    });
  }

  // Filter by search
  if (searchQuery.trim()) {
    const q = searchQuery.toLowerCase();
    displayedFiles = displayedFiles.filter(
      (f) =>
        f.name.toLowerCase().includes(q) ||
        (f.summary && f.summary.toLowerCase().includes(q))
    );
  }

  // File type icon resolver
  const getFileIcon = (fileName, type) => {
    const ext = fileName.split('.').pop().toLowerCase();
    if (ext === 'pdf' || type === 'pdf') {
      return <FileText className="file-icon icon-pdf" size={18} />;
    }
    if (ext === 'xlsx' || ext === 'csv' || ext === 'xls' || type === 'xlsx') {
      return <FileSpreadsheet className="file-icon icon-xlsx" size={18} />;
    }
    if (ext === 'vtt' || ext === 'srt' || ext === 'mp3' || ext === 'wav' || type === 'transcript') {
      return <FileAudio className="file-icon icon-transcript" size={18} />;
    }
    if (ext === 'md' || ext === 'json' || ext === 'jsonl' || type === 'markdown') {
      return <FileCode className="file-icon icon-code" size={18} />;
    }
    return <File className="file-icon icon-default" size={18} />;
  };

  // Handle local file upload to FastAPI backend
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadError(null);

    try {
      const res = await uploadDocumentToBackend(file, file.name);
      const newFileObj = {
        id: res.document_id || `doc_${Date.now()}`,
        name: file.name,
        type: res.file_type || file.name.split('.').pop(),
        size: `${(file.size / 1024).toFixed(1)} KB`,
        status: res.status || 'READY',
        updatedAt: 'Just now',
        summary: res.summary || 'Ingested document into Coordin8 knowledge system.',
        folderId: selectedFolderId || folders[0]?.id,
      };

      onAddFileToProject(project.id, newFileObj, selectedFolderId || folders[0]?.id);
    } catch (err) {
      console.warn('Backend upload failed, saving to local project session:', err.message);
      // Still add locally with client-side representation
      const newFileObj = {
        id: `doc_local_${Date.now()}`,
        name: file.name,
        type: file.name.split('.').pop(),
        size: `${(file.size / 1024).toFixed(1)} KB`,
        status: 'READY',
        updatedAt: 'Just now',
        summary: 'Stored in local project workspace cache.',
        folderId: selectedFolderId || folders[0]?.id,
      };
      onAddFileToProject(project.id, newFileObj, selectedFolderId || folders[0]?.id);
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="file-explorer-container">
      {/* File Explorer Header & Controls */}
      <div className="file-explorer-header">
        <div className="explorer-title-area">
          <div className="folder-crumb-nav">
            <button
              className={`folder-crumb-btn ${!selectedFolderId ? 'active' : ''}`}
              onClick={() => setSelectedFolderId(null)}
            >
              <Folder size={16} />
              <span>All Folders</span>
            </button>
            {activeFolder && (
              <>
                <span className="crumb-sep">/</span>
                <div className="folder-crumb-btn active">
                  <FolderOpen size={16} />
                  <span>{activeFolder.name}</span>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="explorer-actions">
          <div className="search-box">
            <Search size={15} />
            <input
              type="text"
              placeholder="Search files or summaries..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
          />

          <button
            className="btn btn-primary btn-sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            <Upload size={14} />
            <span>{isUploading ? 'Ingesting...' : 'Upload Document'}</span>
          </button>
        </div>
      </div>

      {uploadError && (
        <div className="upload-alert error">{uploadError}</div>
      )}

      {/* Subfolder Chips / Navigation */}
      <div className="subfolder-chips-bar">
        <button
          className={`subfolder-chip ${!selectedFolderId ? 'active' : ''}`}
          onClick={() => setSelectedFolderId(null)}
        >
          <Folder size={14} />
          <span>All Subfolders ({folders.length})</span>
        </button>

        {folders.map((f) => (
          <button
            key={f.id}
            className={`subfolder-chip ${selectedFolderId === f.id ? 'active' : ''}`}
            onClick={() => setSelectedFolderId(f.id)}
          >
            {selectedFolderId === f.id ? <FolderOpen size={14} /> : <Folder size={14} />}
            <span>{f.name}</span>
            <span className="folder-item-count">{f.files?.length || 0}</span>
          </button>
        ))}
      </div>

      {/* Files List Table */}
      <div className="files-table-wrapper">
        <table className="files-table">
          <thead>
            <tr>
              <th style={{ width: '40%' }}>File Name & Summary</th>
              <th style={{ width: '18%' }}>Subfolder</th>
              <th style={{ width: '10%' }}>Size</th>
              <th style={{ width: '14%' }}>Status</th>
              <th style={{ width: '18%' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {displayedFiles.length === 0 ? (
              <tr>
                <td colSpan={5} className="no-files-cell">
                  <div className="empty-files-placeholder">
                    <FileText size={32} />
                    <p>No documents found in this folder</p>
                    <button
                      className="btn btn-outline btn-sm"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Upload size={14} />
                      Upload First File
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              displayedFiles.map((file) => (
                <tr key={file.id} className="file-row">
                  <td>
                    <div className="file-name-cell">
                      {getFileIcon(file.name, file.type)}
                      <div className="file-titles">
                        <span className="file-name">{file.name}</span>
                        {file.summary && (
                          <span className="file-summary-preview" title={file.summary}>
                            {file.summary}
                          </span>
                        )}
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className="folder-tag">
                      <Folder size={12} />
                      {file.folderName || activeFolder?.name || 'General'}
                    </span>
                  </td>
                  <td>
                    <span className="file-size-text">{file.size}</span>
                  </td>
                  <td>
                    <span className={`status-badge status-${file.status?.toLowerCase() || 'ready'}`}>
                      <CheckCircle2 size={12} />
                      {file.status || 'READY'}
                    </span>
                  </td>
                  <td>
                    <div className="file-actions-cell">
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={() => onSelectDoc(file)}
                        title="Inspect Document Provenance & Summary"
                      >
                        <Eye size={14} />
                        <span>Preview</span>
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Backend Connected Documents Section if any */}
      {backendDocs.length > 0 && (
        <div className="backend-sync-banner">
          <HardDrive size={15} />
          <span>
            Connected to Coordin8 DB: <strong>{backendDocs.length}</strong> canonical document records available across system.
          </span>
        </div>
      )}
    </div>
  );
}
