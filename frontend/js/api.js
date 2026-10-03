const API_PROTOCOL = window.location.protocol === 'https:' ? 'https:' : 'http:';
const API_BASE = (window.COORDIN8_API_BASE || document.querySelector('meta[name="coordin8-api-base"]')?.content || `${API_PROTOCOL}//${window.location.hostname || '127.0.0.1'}:8000/api`).replace(/\/$/, '');

const Coordin8Api = (() => {
  let token = sessionStorage.getItem('coordin8-token');

  function clearSession() {
    token = null;
    sessionStorage.removeItem('coordin8-token');
  }

  function errorMessage(detail, status) {
    const defaults = {
      403: 'You do not have permission to perform this action.',
      404: 'The requested item was not found.',
      409: 'This change conflicts with existing data.',
      422: 'Please check the submitted information.',
      429: 'Too many requests. Please wait and try again.',
      500: 'The server encountered an error. Please try again.',
      502: 'The AI service is currently unavailable. Please try again.',
    };
    if (status >= 500 && status !== 502) return defaults[status] || 'The server encountered an error. Please try again.';
    if (typeof detail === 'string' && detail.trim()) return detail;
    if (Array.isArray(detail)) {
      return detail.map(item => {
        const location = Array.isArray(item.loc) ? item.loc.filter(part => part !== 'body').join(' / ') : '';
        return `${location ? `${location}: ` : ''}${item.msg || 'Invalid value'}`;
      }).join(' ');
    }
    return defaults[status] || `Request failed (${status}).`;
  }

  async function request(path, options = {}, authenticated = true) {
    const headers = new Headers(options.headers || {});
    if (authenticated && token) headers.set('Authorization', `Bearer ${token}`);
    if (options.body && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    let response;
    try {
      response = await fetch(`${API_BASE}${path}`, { ...options, headers });
    } catch (cause) {
      const error = new Error('Unable to reach the Coordin8 backend. Check the connection and try again.');
      error.kind = 'network';
      error.cause = cause;
      throw error;
    }

    const contentType = response.headers.get('content-type') || '';
    const data = response.status === 204 ? null : contentType.includes('json')
      ? await response.json().catch(() => null)
      : await response.text().catch(() => '');
    if (!response.ok) {
      if (response.status === 401 && authenticated) {
        clearSession();
        window.dispatchEvent(new Event('coordin8-auth-expired'));
      }
      const detail = typeof data === 'object' && data !== null ? data.detail : data;
      const error = new Error(errorMessage(detail, response.status));
      error.status = response.status;
      throw error;
    }
    return data;
  }

  const json = value => JSON.stringify(value);
  const projectPath = (projectId, suffix = '') => {
    if (!projectId) throw new Error('Select an accessible project first.');
    return `/projects/${encodeURIComponent(projectId)}${suffix}`;
  };

  const api = {
    get: (path, authenticated = true) => request(path, {}, authenticated),
    post: (path, body, authenticated = true) => request(path, { method: 'POST', body: json(body) }, authenticated),
    patch: (path, body) => request(path, { method: 'PATCH', body: json(body) }),
    put: (path, body) => request(path, { method: 'PUT', body: json(body) }),
    delete: path => request(path, { method: 'DELETE' }),
    upload: (path, form) => request(path, { method: 'POST', body: form }),
    get token() { return token; },
    async login(email, password) {
      const result = await api.post('/auth/login', { email, password }, false);
      token = result.access_token;
      sessionStorage.setItem('coordin8-token', token);
      try {
        return await api.me();
      } catch (error) {
        clearSession();
        throw error;
      }
    },
    me: () => api.get('/auth/me'),
    logout: clearSession,
    health: () => api.get('/health', false),
    projects: () => api.get('/projects'),
    createProject: project => api.post('/projects', project),
    getProject: id => api.get(`/projects/${encodeURIComponent(id)}`),
    updateProject: (id, changes) => api.patch(`/projects/${encodeURIComponent(id)}`, changes),
    documents: projectId => api.get(projectPath(projectId, '/documents')),
    uploadDocument: (form, projectId) => api.upload(projectPath(projectId, '/documents'), form),
    chat: (message, projectId) => api.post(`${projectPath(projectId)}/chat`, { message }),
    search: (query, projectId, limit = 10) => api.post(`${projectPath(projectId)}/search`, { query, limit }),
    hierarchy: (documentId, projectId) => api.get(`${projectPath(projectId, `/documents/${encodeURIComponent(documentId)}/hierarchy`)}`),
    dashboard: () => api.get('/dashboard'),
    projectDashboard: projectId => api.get(projectPath(projectId, '/dashboard')),
    tasks: projectId => api.get(projectPath(projectId, '/tasks')),
    createTask: (task, projectId) => api.post(projectPath(projectId, '/tasks'), task),
    updateTask: (id, changes) => api.patch(`/tasks/${encodeURIComponent(id)}`, changes),
    meetings: projectId => api.get(projectPath(projectId, '/meetings')),
    uploadMeeting: (form, projectId) => api.upload(projectPath(projectId, '/meetings'), form),
    generateMom: id => api.post(`/meetings/${encodeURIComponent(id)}/generate-mom`),
    actionItemToTask: id => api.post(`/action-items/${encodeURIComponent(id)}/tasks`),
    employees: () => api.get('/employees'),
    createEmployee: employee => api.post('/employees', employee),
    updateEmployee: (id, changes) => api.patch(`/employees/${encodeURIComponent(id)}`, changes),
    projectMembers: projectId => api.get(projectPath(projectId, '/members')),
    getProjectMembers: projectId => api.get(projectPath(projectId, '/members')),
    addProjectMember: (projectId, userId) => api.post(projectPath(projectId, '/members'), { user_id: userId }),
    removeProjectMember: (projectId, userId) => api.delete(`${projectPath(projectId, '/members')}/${encodeURIComponent(userId)}`),
    weeklyReport: projectId => api.get(projectPath(projectId, '/reports/weekly')),
    jiraMetrics: projectId => api.get(projectPath(projectId, '/jira-metrics')),
  };

  return api;
})();