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
    const projects = (data.projects || []).map((p) => ({
      ...p,
      id: p.project_id || p.id,
    }));
    const unassigned_meetings = data.unassigned_meetings || [];
    return { projects, unassigned_meetings };
  } catch (err) {
    console.warn('Could not fetch projects from backend:', err.message);
    return null; // indicates offline / fallback
  }
}

export async function fetchUnassignedMeetings() {
  try {
    const res = await fetch(`${API_BASE}/projects/meetings/unassigned`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    return data.meetings || [];
  } catch (err) {
    console.warn('Could not fetch unassigned meetings:', err.message);
    return [];
  }
}

export async function addUnassignedMeeting(meeting) {
  try {
    const res = await fetch(`${API_BASE}/projects/meetings/unassigned`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(meeting),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not add unassigned meeting:', err.message);
    return null;
  }
}

export async function batchAddUnassignedMeetings(meetings) {
  try {
    const res = await fetch(`${API_BASE}/projects/meetings/unassigned/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(meetings),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not batch add unassigned meetings:', err.message);
    return null;
  }
}

export async function deleteUnassignedMeeting(meetingId) {
  try {
    const res = await fetch(`${API_BASE}/projects/meetings/unassigned/${encodeURIComponent(meetingId)}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not delete unassigned meeting:', err.message);
    return null;
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

export async function addProjectMeeting(projectId, meeting) {
  try {
    const res = await fetch(`${API_BASE}/projects/${projectId}/meetings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(meeting),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not persist meeting to backend:', err.message);
    return null;
  }
}

export async function batchAddProjectMeetings(projectId, meetings) {
  try {
    const res = await fetch(`${API_BASE}/projects/${projectId}/meetings/batch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(meetings),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not batch persist meetings to backend:', err.message);
    return null;
  }
}

export async function deleteProjectMeeting(projectId, meetingId) {
  try {
    const res = await fetch(`${API_BASE}/projects/${projectId}/meetings/${encodeURIComponent(meetingId)}`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not delete meeting on backend:', err.message);
    return null;
  }
}

export async function fetchGcalAccount() {
  try {
    const res = await fetch(`${API_BASE}/projects/gcal_account`, { signal: AbortSignal.timeout(3000) });
    if (!res.ok) return null;
    const data = await res.json();
    return data.account || null;
  } catch (err) {
    console.warn('Could not fetch gcal account from backend:', err.message);
    return null;
  }
}

export async function saveGcalAccount(accountData) {
  try {
    const res = await fetch(`${API_BASE}/projects/gcal_account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(accountData),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not persist gcal account to backend:', err.message);
    return null;
  }
}

export async function deleteGcalAccount() {
  try {
    const res = await fetch(`${API_BASE}/projects/gcal_account`, {
      method: 'DELETE',
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not delete gcal account on backend:', err.message);
    return null;
  }
}



