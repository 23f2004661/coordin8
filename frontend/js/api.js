const API_BASE = `http://${window.location.hostname || 'localhost'}:8000/api`;

const Coordin8Api = (() => {
  let token = sessionStorage.getItem('coordin8-token');
  let activeProjectId = sessionStorage.getItem('coordin8-project');

  async function request(path, options = {}, authenticated = true) {
    const headers = new Headers(options.headers || {});
    if (authenticated && token) headers.set('Authorization', `Bearer ${token}`);
    if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      if (response.status === 401 && authenticated) {
        clearSession();
        window.dispatchEvent(new Event('coordin8-auth-expired'));
      }
      if (response.status === 403) {
        throw new Error("You don't have permission to access this project.");
      }
      throw new Error(data.detail || `Request failed (${response.status})`);
    }
    return data;
  }

  function clearSession() {
    token = null;
    activeProjectId = null;
    sessionStorage.removeItem('coordin8-token');
    sessionStorage.removeItem('coordin8-project');
  }

  function requireProject() {
    if (!activeProjectId) throw new Error('Select an accessible project first.');
    return activeProjectId;
  }

  return {
    get token() { return token; },
    get activeProjectId() { return activeProjectId; },
    setActiveProject(id) {
      activeProjectId = id || null;
      if (activeProjectId) sessionStorage.setItem('coordin8-project', activeProjectId);
      else sessionStorage.removeItem('coordin8-project');
    },
    async login(email, password) {
      const result = await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }, false);
      token = result.access_token;
      sessionStorage.setItem('coordin8-token', token);
      try {
        return await this.me();
      } catch (error) {
        clearSession();
        throw error;
      }
    },
    me: () => request('/auth/me'),
    logout() { clearSession(); },
    health: () => request('/health', {}, false),
    projects: () => request('/projects'),
    createProject: project => request('/projects', { method: 'POST', body: JSON.stringify(project) }),
    getProject: id => request(`/projects/${encodeURIComponent(id)}`),
    updateProject: (id, changes) => request(`/projects/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(changes) }),
    documents: () => request(`/projects/${requireProject()}/documents`),
    uploadDocument: form => request(`/projects/${requireProject()}/documents`, { method: 'POST', body: form }),
    chat: message => request(`/projects/${requireProject()}/chat`, { method: 'POST', body: JSON.stringify({ message }) }),
    search: (query, limit = 10) => request(`/projects/${requireProject()}/search`, { method: 'POST', body: JSON.stringify({ query, limit }) }),
    hierarchy: documentId => request(`/projects/${requireProject()}/documents/${encodeURIComponent(documentId)}/hierarchy`),
    dashboard: () => request('/dashboard'),
    projectDashboard: () => request(`/projects/${requireProject()}/dashboard`),
    tasks: () => request(`/projects/${requireProject()}/tasks`),
    createTask: task => request(`/projects/${requireProject()}/tasks`, { method: 'POST', body: JSON.stringify(task) }),
    updateTask: (id, changes) => request(`/tasks/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(changes) }),
    meetings: () => request(`/projects/${requireProject()}/meetings`),
    uploadMeeting: form => request(`/projects/${requireProject()}/meetings`, { method: 'POST', body: form }),
    generateMom: id => request(`/meetings/${encodeURIComponent(id)}/generate-mom`, { method: 'POST' }),
    actionItemToTask: id => request(`/action-items/${encodeURIComponent(id)}/tasks`, { method: 'POST' }),
    employees: () => request('/employees'),
    createEmployee: employee => request('/employees', { method: 'POST', body: JSON.stringify(employee) }),
    updateEmployee: (id, changes) => request(`/employees/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(changes) }),
    projectMembers: () => request(`/projects/${requireProject()}/members`),
    getProjectMembers: projectId => request(`/projects/${encodeURIComponent(projectId)}/members`),
    addProjectMember: (projectId, userId) => request(`/projects/${encodeURIComponent(projectId)}/members`, { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
    removeProjectMember: (projectId, userId) => request(`/projects/${encodeURIComponent(projectId)}/members/${encodeURIComponent(userId)}`, { method: 'DELETE' }),
    weeklyReport: () => request(`/projects/${requireProject()}/reports/weekly`),
    jiraMetrics: () => request(`/projects/${requireProject()}/jira-metrics`),
  };
})();