/**
 * API service for Coordin8 Backend communication and Local State.
 */

const API_BASE = '/api';

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return { online: true, data };
  } catch (err) {
    return { online: false, error: err.message };
  }
}

export async function fetchBackendDocuments() {
  try {
    const res = await fetch(`${API_BASE}/documents`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not fetch documents from backend:', err.message);
    return [];
  }
}

export async function uploadDocumentToBackend(file, title = '') {
  const formData = new FormData();
  formData.append('file', file);
  if (title) formData.append('title', title);

  const res = await fetch(`${API_BASE}/documents`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Upload failed with HTTP ${res.status}`);
  }
  return await res.json();
}

export async function fetchDocumentDetail(docId) {
  const res = await fetch(`${API_BASE}/documents/${docId}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function fetchHomeFolder() {
  try {
    const res = await fetch(`${API_BASE}/projects/home_folder`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      home_folder: 'C:\\Users\\ssrin\\Desktop\\Coordin8 Home',
      exists: true,
      existing_folders: [],
    };
  }
}

export async function fetchProjectsFromBackend() {
  try {
    const res = await fetch(`${API_BASE}/projects`, { signal: AbortSignal.timeout(4000) });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.projects || [];
  } catch (err) {
    console.warn('Could not fetch projects from backend:', err.message);
    return null; // indicates offline / fallback
  }
}

export async function createProjectOnBackend(payload) {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create project: HTTP ${res.status}`);
  }
  return await res.json();
}

export async function rescanProjectOnBackend(projectId) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/rescan`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

export async function searchProjectKnowledge(projectId, query) {
  const res = await fetch(`${API_BASE}/projects/${projectId}/search?query=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}
