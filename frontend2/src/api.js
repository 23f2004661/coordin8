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

/**
 * Upload a meeting transcript and index it in project or general KB.
 */
export async function uploadMeetingTranscript(meetingId, file, projectId = null) {
  const formData = new FormData();
  formData.append('file', file);
  if (projectId) {
    formData.append('project_id', projectId);
  }

  const res = await fetch(`${API_BASE}/projects/meetings/${encodeURIComponent(meetingId)}/transcript`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Upload failed with HTTP ${res.status}`);
  }
  return await res.json();
}

/**
 * Retrieve synchronized emails from backend.
 */
export async function fetchSyncedEmails() {
  try {
    const res = await fetch(`${API_BASE}/projects/emails`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.emails || [];
  } catch (err) {
    console.warn('Could not fetch emails from backend:', err.message);
    return [];
  }
}

/**
 * Persist synchronized emails to backend.
 */
export async function syncEmailsWithBackend(emails) {
  try {
    const res = await fetch(`${API_BASE}/projects/emails/sync`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ emails }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not sync emails to backend:', err.message);
    return null;
  }
}

/**
 * Create a deliverable on backend.
 */
export async function createProjectDeliverable(projectId, deliverable) {
  try {
    const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/deliverables`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(deliverable),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not create deliverable on backend:', err.message);
    return null;
  }
}

/**
 * Update a deliverable status on backend.
 */
export async function updateProjectDeliverable(projectId, deliverableId, updates) {
  try {
    const res = await fetch(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/deliverables/${encodeURIComponent(deliverableId)}`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      }
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not update deliverable on backend:', err.message);
    return null;
  }
}

/**
 * Delete a deliverable from a project.
 */
export async function deleteProjectDeliverable(projectId, deliverableId) {
  try {
    const res = await fetch(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/deliverables/${encodeURIComponent(deliverableId)}`,
      { method: 'DELETE' }
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not delete deliverable on backend:', err.message);
    return null;
  }
}

/**
 * Trigger AI task breakdown on a deliverable.
 */
export async function breakdownDeliverable(projectId, deliverableId) {
  const res = await fetch(
    `${API_BASE}/projects/${encodeURIComponent(projectId)}/deliverables/${encodeURIComponent(deliverableId)}/breakdown`,
    { method: 'POST' }
  );
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Breakdown failed with HTTP ${res.status}`);
  }
  return await res.json();
}

/**
 * Fetch all execution tasks for a project.
 */
export async function fetchProjectTasks(projectId) {
  try {
    const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/tasks`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not fetch project tasks:', err.message);
    return { tasks: [] };
  }
}

/**
 * Update an execution task status or stage.
 */
export async function updateProjectTask(projectId, deliverableId, taskId, updates) {
  try {
    const res = await fetch(
      `${API_BASE}/projects/${encodeURIComponent(projectId)}/deliverables/${encodeURIComponent(deliverableId)}/tasks/${encodeURIComponent(taskId)}`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      }
    );
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not update task on backend:', err.message);
    return null;
  }
}

/**
 * Update project strategic attributes (problem statement, background context, client info).
 */
export async function updateProjectOnBackend(projectId, updates) {
  try {
    const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('Could not update project on backend:', err.message);
    return null;
  }
}

/**
 * Trigger AI deliverable progress audit and candidate milestone discovery.
 */
export async function analyzeProjectDeliverables(projectId) {
  const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/analyze-deliverables`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Analysis failed with HTTP ${res.status}`);
  }
  return await res.json();
}

/**
 * Accept an AI-discovered candidate deliverable into official project timeline.
 */
export async function acceptDiscoveredDeliverable(projectId, candidate) {
  const res = await fetch(
    `${API_BASE}/projects/${encodeURIComponent(projectId)}/deliverables/accept-discovered`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(candidate),
    }
  );
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to accept deliverable: HTTP ${res.status}`);
  }
  return await res.json();
}

/**
 * Dismiss an AI-discovered candidate deliverable.
 */
export async function dismissDiscoveredDeliverable(projectId, title) {
  const res = await fetch(
    `${API_BASE}/projects/${encodeURIComponent(projectId)}/deliverables/dismiss-discovered`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    }
  );
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

/**
 * Assign or unassign an email to a project and run AI archetype classification.
 */
export async function assignEmailToProject(emailId, projectId) {
  const res = await fetch(`${API_BASE}/projects/emails/${encodeURIComponent(emailId)}/assign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ projectId }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to assign email: HTTP ${res.status}`);
  }
  return await res.json();
}

/**
 * Open any file (Excel, Word, PDF, text, markdown) in its native OS desktop application.
 */
export async function openFileInNativeApp({ filePath, projectId, fileName } = {}) {
  const res = await fetch(`${API_BASE}/projects/open-file`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_path: filePath || null,
      project_id: projectId || null,
      file_name: fileName || null,
    }),
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to open file: HTTP ${res.status}`);
  }
  return await res.json();
}

/**
 * Open the physical project folder in Windows Explorer.
 */
export async function openProjectFolderInNativeOS(projectId) {
  const res = await fetch(`${API_BASE}/projects/${encodeURIComponent(projectId)}/open-folder`, {
    method: 'POST',
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || `Failed to open project folder: HTTP ${res.status}`);
  }
  return await res.json();
}
