/**
 * Coordin8 Frontend Client
 * Implements Dashboard, Document Management, Search & Grounded Answer, and Developer Inspector
 */

// Global constants
let appInitialized = false;
let activeUser = null;
let accessibleProjects = [];
let chatUploadInProgress = false;

document.addEventListener('DOMContentLoaded', () => {
  initAuthentication();
});

function initAuthentication() {
  const loginForm = document.getElementById('login-form');
  const logoutButton = document.getElementById('logout-button');
  if (loginForm) {
    loginForm.addEventListener('submit', async event => {
      event.preventDefault();
      const form = new FormData(loginForm);
      const error = document.getElementById('login-error');
      if (error) error.textContent = '';
      try {
        const user = await Coordin8Api.login(form.get('email'), form.get('password'));
        loginForm.reset();
        await startAuthenticatedApp(user);
      } catch (err) {
        if (error) error.textContent = err.message;
      }
    });
  }
  if (logoutButton) logoutButton.addEventListener('click', logout);
  window.addEventListener('coordin8-auth-expired', () => showLogin('Your session has expired. Please sign in again.'));
  if (Coordin8Api.token) {
    Coordin8Api.me().then(startAuthenticatedApp).catch(() => showLogin());
  } else showLogin();
}

async function startAuthenticatedApp(user) {
  activeUser = user;
  accessibleProjects = user.projects || [];
  document.body.classList.add('authenticated');
  window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#/dashboard`);
  const userName = document.getElementById('user-name');
  const userRole = document.getElementById('user-role');
  if (userName) userName.textContent = user.name;
  if (userRole) userRole.textContent = user.role.replaceAll('_', ' ');

  const projectSelect = document.getElementById('active-project');
  const savedProject = Coordin8Api.activeProjectId;
  if (projectSelect) {
    projectSelect.innerHTML = accessibleProjects.map(project =>
      `<option value="${escapeHtml(project.id)}">${escapeHtml(project.name)}</option>`
    ).join('');
    projectSelect.hidden = accessibleProjects.length === 0;
    projectSelect.disabled = accessibleProjects.length < 2;
    const selected = accessibleProjects.some(project => project.id === savedProject) ? savedProject : accessibleProjects[0]?.id;
    Coordin8Api.setActiveProject(selected);
    if (selected) projectSelect.value = selected;
    if (!projectSelect.dataset.bound) {
      projectSelect.addEventListener('change', async () => {
        Coordin8Api.setActiveProject(projectSelect.value);
        updateActiveProjectName();
        clearProjectChat();
        await refreshProjectViews();
        if (activeUser.role === 'ADMIN') await loadAdminManagement();
      });
      projectSelect.dataset.bound = 'true';
    }
  }

  applyRoleNavigation(user.role);
  const documentDropzone = document.getElementById('file-dropzone');
  if (documentDropzone) documentDropzone.hidden = !['ADMIN', 'MANAGER'].includes(user.role);
  const chatAttachButton = document.getElementById('chat-attach-button');
  if (chatAttachButton) chatAttachButton.hidden = !['ADMIN', 'MANAGER'].includes(user.role);
  updateActiveProjectName();
  if (!appInitialized) {
    initNavigation();
    initProjectChat();
    initUpload();
    initAdminManagement();
    initProjectWorkflowViews();
    appInitialized = true;
  }
  if (user.role === 'ADMIN') await loadAdminManagement();
  await refreshProjectViews();
  checkServerStatus();
}

function showLogin(message = '') {
  document.body.classList.remove('authenticated');
  window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#/login`);
  const error = document.getElementById('login-error');
  if (error) error.textContent = message;
}

function logout() {
  Coordin8Api.logout();
  showLogin();
}

function initAdminManagement() {
  const projectForm = document.getElementById('create-project-form');
  const employeeForm = document.getElementById('create-employee-form');
  if (projectForm && !projectForm.dataset.bound) {
    projectForm.addEventListener('submit', async event => {
      event.preventDefault();
      const fields = new FormData(projectForm);
      try {
        await Coordin8Api.createProject({ name: fields.get('name'), client: fields.get('client') || null });
        projectForm.reset();
        const user = await Coordin8Api.me();
        renderProjectOptions(user.projects);
        await refreshProjectViews();
        await loadAdminManagement();
      } catch (error) {
        window.alert(error.message);
      }
    });
    projectForm.dataset.bound = 'true';
  }
  if (employeeForm && !employeeForm.dataset.bound) {
    employeeForm.addEventListener('submit', async event => {
      event.preventDefault();
      const fields = new FormData(employeeForm);
      const status = document.getElementById('employee-form-status');
      try {
        await Coordin8Api.createEmployee({
          name: fields.get('name'),
          email: fields.get('email'),
          temporary_password: fields.get('temporary_password'),
          role: fields.get('role'),
          project_ids: fields.getAll('project_ids'),
        });
        employeeForm.reset();
        if (status) status.textContent = 'Employee created.';
        await loadAdminManagement();
      } catch (error) {
        if (status) status.textContent = error.message;
      }
    });
    employeeForm.dataset.bound = 'true';
  }
}

async function loadAdminManagement() {
  setViewState('admin-projects', 'loading', 'Loading tenant projects...');
  setViewState('employees', 'loading', 'Loading employees...');
  try {
    const [projects, employees] = await Promise.all([Coordin8Api.projects(), Coordin8Api.employees()]);
    const employeeProjects = document.getElementById('employee-projects');
    const employeeRows = document.getElementById('employees-tbody');
    const projectRows = document.getElementById('admin-projects-tbody');
    const projectMembers = await Promise.all(projects.map(project => Coordin8Api.getProjectMembers(project.id).catch(() => [])));
    if (projectRows) {
      projectRows.innerHTML = projects.length ? projects.map((project, index) => {
        const members = projectMembers[index];
        const activeEmployees = employees.filter(employee => employee.is_active && !members.some(member => member.user_id === employee.id));
        return `<tr>
          <td><strong>${escapeHtml(project.name)}</strong></td>
          <td>${escapeHtml(project.client || '—')}</td>
          <td>${escapeHtml(project.status)}</td>
          <td>${members.length ? members.map(member => `<span class="member-chip">${escapeHtml(member.name)}<button type="button" class="remove-member" data-project-id="${escapeHtml(project.id)}" data-user-id="${escapeHtml(member.user_id)}" aria-label="Remove ${escapeHtml(member.name)}">×</button></span>`).join('') : '<span class="muted-label">No members</span>'}</td>
          <td><div class="member-assignment"><select class="input-text member-select" data-project-id="${escapeHtml(project.id)}"><option value="">Select employee</option>${activeEmployees.map(employee => `<option value="${escapeHtml(employee.id)}">${escapeHtml(employee.name)}</option>`).join('')}</select><button class="btn btn-secondary add-member" data-project-id="${escapeHtml(project.id)}" type="button" aria-label="Add member">Add</button></div></td>
        </tr>`;
      }).join('') : '<tr><td colspan="5" class="table-empty">No projects found for this tenant.</td></tr>';
      projectRows.querySelectorAll('.add-member').forEach(button => button.addEventListener('click', async () => {
        const select = projectRows.querySelector(`.member-select[data-project-id="${button.dataset.projectId}"]`);
        if (!select?.value) return;
        try {
          await Coordin8Api.addProjectMember(button.dataset.projectId, select.value);
          await loadAdminManagement();
          await refreshProjectViews();
        } catch (error) {
          setViewState('admin-projects', 'error', error.message);
        }
      }));
      projectRows.querySelectorAll('.remove-member').forEach(button => button.addEventListener('click', async () => {
        try {
          await Coordin8Api.removeProjectMember(button.dataset.projectId, button.dataset.userId);
          await loadAdminManagement();
          await refreshProjectViews();
        } catch (error) {
          setViewState('admin-projects', 'error', error.message);
        }
      }));
      setViewState('admin-projects', projects.length ? 'clear' : 'empty', 'No projects found for this tenant.');
    }
    if (employeeProjects) {
      employeeProjects.innerHTML = projects.map(project =>
        `<option value="${escapeHtml(project.id)}">${escapeHtml(project.name)}</option>`
      ).join('');
    }
    if (employeeRows) {
      employeeRows.innerHTML = employees.map(employee => {
        const names = projects.filter(project => employee.project_ids.includes(project.id)).map(project => project.name).join(', ');
        const isCurrentUser = employee.id === activeUser.id;
        const roleControl = employee.role === 'ADMIN' || isCurrentUser
          ? escapeHtml(employee.role)
          : `<select class="input-text employee-role" data-id="${escapeHtml(employee.id)}"><option value="MANAGER" ${employee.role === 'MANAGER' ? 'selected' : ''}>MANAGER</option><option value="TEAM_MEMBER" ${employee.role === 'TEAM_MEMBER' ? 'selected' : ''}>TEAM_MEMBER</option></select>`;
        const accountAction = isCurrentUser ? '<span class="muted-label">Current account</span>' : `<button class="btn btn-secondary employee-toggle" data-id="${escapeHtml(employee.id)}" data-active="${employee.is_active}">${employee.is_active ? 'Deactivate' : 'Activate'}</button>`;
        return `<tr><td>${escapeHtml(employee.name)}</td><td>${escapeHtml(employee.email)}</td><td>${roleControl}</td><td>${escapeHtml(names || '—')}</td><td>${employee.is_active ? 'Active' : 'Inactive'}</td><td>${accountAction}</td></tr>`;
      }).join('');
      employeeRows.querySelectorAll('.employee-role').forEach(select => {
        select.addEventListener('change', async () => {
          try {
            await Coordin8Api.updateEmployee(select.dataset.id, { role: select.value });
            await loadAdminManagement();
          } catch (error) {
            window.alert(error.message);
          }
        });
      });
      employeeRows.querySelectorAll('.employee-toggle').forEach(button => {
        button.addEventListener('click', async () => {
          try {
            await Coordin8Api.updateEmployee(button.dataset.id, { is_active: button.dataset.active !== 'true' });
            await loadAdminManagement();
          } catch (error) {
            window.alert(error.message);
          }
        });
      });
      setViewState('employees', employees.length ? 'clear' : 'empty', 'No employees found.');
    }
  } catch (error) {
    setViewState('employees', 'error', 'Unable to load tenant administration. Please try again.');
    setViewState('admin-projects', 'error', 'Unable to load tenant projects. Please try again.');
  }
}

function renderProjectOptions(projects) {
  accessibleProjects = projects;
  const selector = document.getElementById('active-project');
  if (!selector) return;
  const current = Coordin8Api.activeProjectId;
  selector.innerHTML = projects.map(project => `<option value="${escapeHtml(project.id)}">${escapeHtml(project.name)}</option>`).join('');
  selector.hidden = projects.length === 0;
  selector.disabled = projects.length < 2;
  const selected = projects.some(project => project.id === current) ? current : projects[0]?.id;
  Coordin8Api.setActiveProject(selected);
  if (selected) selector.value = selected;
  updateActiveProjectName();
}

function applyRoleNavigation(role) {
  document.querySelectorAll('.nav-item[data-roles]').forEach(item => {
    const roles = item.dataset.roles.split(',');
    item.hidden = !roles.includes(role);
  });
  const firstVisible = [...document.querySelectorAll('.nav-item[data-view]')].find(item => !item.hidden);
  if (firstVisible && !document.querySelector('.nav-item.active:not([hidden])')) firstVisible.click();
}

function updateActiveProjectName() {
  const project = accessibleProjects.find(item => item.id === Coordin8Api.activeProjectId);
  const projectLabel = document.getElementById('active-project-name');
  const selector = document.getElementById('active-project');
  const dashboardTitle = document.getElementById('dashboard-project-title');
  const displayName = project?.name || 'Select a project';
  if (projectLabel) projectLabel.textContent = displayName;
  if (selector) selector.setAttribute('aria-label', `Active project: ${displayName}`);
  if (dashboardTitle) dashboardTitle.textContent = displayName.toUpperCase();
  ['documents-project-name', 'meetings-project-name', 'team-project-name', 'report-project-name', 'chat-project-name', 'chat-scope-project-name'].forEach(id => {
    const node = document.getElementById(id);
    if (node) node.textContent = project?.name || 'No project selected';
  });
}

function initProjectWorkflowViews() {
  const taskForm = document.getElementById('create-task-form');
  const meetingForm = document.getElementById('meeting-upload-form');
  if (taskForm && !taskForm.dataset.bound) {
    taskForm.addEventListener('submit', async event => {
      event.preventDefault();
      const fields = new FormData(taskForm);
      try {
        await Coordin8Api.createTask({
          title: fields.get('title'),
          owner_id: fields.get('owner_id') || null,
          due_date: fields.get('due_date') || null,
        });
        taskForm.reset();
        await refreshProjectViews();
        await initDocumentsTable();
      } catch (error) {
        window.alert(error.message);
      }
    });
    taskForm.dataset.bound = 'true';
  }
  if (meetingForm && !meetingForm.dataset.bound) {
    meetingForm.addEventListener('submit', async event => {
      event.preventDefault();
      const status = document.getElementById('meeting-form-status');
      try {
        await Coordin8Api.uploadMeeting(new FormData(meetingForm));
        meetingForm.reset();
        if (status) status.textContent = 'Transcript uploaded and indexed.';
        await refreshProjectViews();
      } catch (error) {
        if (status) status.textContent = error.message;
      }
    });
    meetingForm.dataset.bound = 'true';
  }
}

async function refreshProjectViews() {
  const projectId = Coordin8Api.activeProjectId;
  const views = ['dashboard', 'deliverables', 'documents', 'meetings', 'team', 'reports', 'jira'];
  if (!projectId) {
    views.forEach(view => setViewState(view, 'empty', 'Select an accessible project to view this information.'));
    if (activeUser?.role === 'ADMIN') {
      setViewState('dashboard', 'loading', 'Loading tenant overview...');
      try {
        const tenantDashboard = await Coordin8Api.dashboard();
        renderDashboard(
          { tasks: { total: 0, backlog: 0, in_progress: 0, review: 0, done: 0, at_risk: 0 }, upcoming_tasks: [] },
          tenantDashboard,
          [],
          [],
        );
        setViewState('dashboard', 'clear');
      } catch {
        setViewState('dashboard', 'error', 'Unable to load tenant dashboard. Please try again.');
      }
    }
    return;
  }
  const canManage = activeUser && ['ADMIN', 'MANAGER'].includes(activeUser.role);
  const taskForm = document.getElementById('create-task-form');
  if (taskForm) taskForm.hidden = !canManage;
  const meetingForm = document.getElementById('meeting-upload-form');
  if (meetingForm) meetingForm.hidden = !canManage;
  views.forEach(view => setViewState(view, 'loading', `Loading ${view === 'jira' ? 'Jira metrics' : view}...`));

  const requests = [
    Coordin8Api.projectDashboard(),
    Coordin8Api.dashboard(),
    Coordin8Api.tasks(),
    Coordin8Api.meetings(),
    Coordin8Api.projectMembers(),
    Coordin8Api.weeklyReport(),
    Coordin8Api.documents(),
    activeUser?.role === 'MANAGER' ? Coordin8Api.jiraMetrics() : Promise.resolve(null),
  ];
  const results = await Promise.allSettled(requests);
  const loaded = {};
  const requestNames = ['projectDashboard', 'roleDashboard', 'tasks', 'meetings', 'members', 'report', 'documents', 'jira'];
  results.forEach((item, index) => { loaded[requestNames[index]] = item; });

  const tasks = loaded.tasks.status === 'fulfilled' ? loaded.tasks.value : [];
  const meetings = loaded.meetings.status === 'fulfilled' ? loaded.meetings.value : [];
  const members = loaded.members.status === 'fulfilled' ? loaded.members.value : [];
  renderTasks(tasks);
  renderMeetings(meetings, canManage);
  renderTeam(members);
  renderTaskOwners(members);
  if (loaded.projectDashboard.status === 'fulfilled' && loaded.roleDashboard.status === 'fulfilled') {
    renderDashboard(loaded.projectDashboard.value, loaded.roleDashboard.value, tasks, meetings);
    setViewState('dashboard', tasks.length ? 'clear' : 'empty', 'No project tasks or meetings yet.');
  } else {
    setViewState('dashboard', 'error', 'Unable to load project dashboard. Please try again.');
  }
  if (loaded.tasks.status === 'fulfilled') {
    setViewState('deliverables', tasks.length ? 'clear' : 'empty', 'No tasks found for this project.');
    renderTimeline(tasks);
  } else setViewState('deliverables', 'error', 'Unable to load project tasks. Please try again.');
  if (loaded.meetings.status === 'fulfilled') setViewState('meetings', meetings.length ? 'clear' : 'empty', 'No meetings found for this project.');
  else setViewState('meetings', 'error', 'Unable to load project meetings. Please try again.');
  if (loaded.members.status === 'fulfilled') setViewState('team', members.length ? 'clear' : 'empty', 'No team members are assigned to this project.');
  else setViewState('team', 'error', 'Unable to load project team. Please try again.');
  if (loaded.report.status === 'fulfilled') {
    renderWeeklyReport(loaded.report.value);
    setViewState('reports', 'clear');
  } else setViewState('reports', 'error', 'Unable to load the weekly report. Please try again.');
  if (loaded.documents.status === 'fulfilled') {
    renderDocumentsView(loaded.documents.value);
    setViewState('documents', loaded.documents.value.length ? 'clear' : 'empty', 'No documents found for this project.');
  } else setViewState('documents', 'error', 'Unable to load project documents. Please try again.');
  if (activeUser?.role === 'MANAGER' && loaded.jira.status === 'fulfilled') {
    renderJiraMetrics(loaded.jira.value);
    setViewState('jira', 'clear');
  } else if (activeUser?.role === 'MANAGER') setViewState('jira', 'error', 'Unable to load demo Jira metrics. Please try again.');
}

function setViewState(view, state, message = '') {
  const node = document.getElementById(`${view}-state`);
  if (!node) return;
  node.hidden = state === 'clear';
  node.dataset.state = state;
  node.textContent = message;
}

function renderDashboard(projectDashboard, roleDashboard, tasks, meetings) {
  const totals = { ...projectDashboard.tasks };
  if (activeUser.role === 'ADMIN') Object.assign(totals, roleDashboard.tasks);
  if (activeUser.role === 'TEAM_MEMBER') {
    ['backlog', 'in_progress', 'review', 'done'].forEach(status => {
      totals[status] = tasks.filter(task => task.status === status.toUpperCase()).length;
    });
    totals.total = tasks.length;
    totals.at_risk = tasks.filter(task => task.risk).length;
  }
  const mine = tasks.filter(task => task.owner_id === activeUser.id);
  const riskCount = activeUser.role === 'ADMIN'
    ? roleDashboard.at_risk_projects.length
    : tasks.filter(task => task.risk).length;
  const riskIndicator = document.getElementById('dashboard-risk-indicator');
  if (riskIndicator) {
    riskIndicator.textContent = riskCount ? `${riskCount} ${activeUser.role === 'ADMIN' ? 'projects' : 'tasks'} at risk` : 'On track';
    riskIndicator.classList.toggle('is-at-risk', riskCount > 0);
  }

  const myTaskCount = document.getElementById('my-task-count');
  const myTaskTitle = document.getElementById('my-task-title');
  const myTaskList = document.getElementById('my-task-list');
  if (myTaskTitle) myTaskTitle.textContent = activeUser.role === 'ADMIN' ? 'Tenant Overview' : 'My Tasks';
  if (myTaskCount) myTaskCount.textContent = activeUser.role === 'ADMIN' ? roleDashboard.employee_count : mine.length;
  if (myTaskList) {
    if (activeUser.role === 'ADMIN') {
      myTaskList.innerHTML = `<div class="dashboard-metric-line"><span>Employees</span><strong>${roleDashboard.employee_count}</strong></div><div class="dashboard-metric-line"><span>Tenant projects</span><strong>${roleDashboard.project_count}</strong></div><div class="dashboard-metric-line"><span>Active projects</span><strong>${roleDashboard.active_projects}</strong></div>`;
    } else if (!mine.length) {
      myTaskList.innerHTML = '<div class="inline-empty">No tasks assigned to you.</div>';
    } else {
      myTaskList.innerHTML = mine.slice(0, 4).map(task => `<div class="task-progress-row"><span class="status-dot-sm status-${task.status.toLowerCase()}"></span><span class="task-progress-title">${escapeHtml(task.title)}</span><span class="muted-label">${escapeHtml(task.due_date || 'No due date')}</span></div>`).join('');
    }
  }

  const total = totals.total || 0;
  const statusCounts = [
    ['BACKLOG', totals.backlog || 0, 'var(--status-backlog)'],
    ['IN PROGRESS', totals.in_progress || 0, 'var(--status-progress)'],
    ['REVIEW', totals.review || 0, 'var(--status-review)'],
    ['DONE', totals.done || 0, 'var(--status-done)'],
  ];
  let cursor = 0;
  const segments = statusCounts.map(([, count, color]) => {
    const start = cursor;
    cursor += total ? count / total * 100 : 0;
    return `${color} ${start}% ${cursor}%`;
  });
  const donut = document.getElementById('task-donut');
  if (donut) donut.style.background = total ? `conic-gradient(${segments.join(', ')})` : 'conic-gradient(var(--border-subtle) 0 100%)';
  const donutTotal = document.getElementById('task-donut-total');
  if (donutTotal) donutTotal.textContent = total;
  const totalLabel = document.getElementById('task-total-label');
  if (totalLabel) totalLabel.textContent = `${total} total`;
  const legend = document.getElementById('task-chart-legend');
  if (legend) legend.innerHTML = statusCounts.map(([label, count, color]) => `<div class="legend-row"><span class="legend-swatch" style="background:${color}"></span><span>${label}</span><strong>${count}</strong></div>`).join('');

  const completion = total ? Math.round((totals.done || 0) / total * 100) : 0;
  const completionPercent = document.getElementById('completion-percent');
  const completionBar = document.getElementById('completion-bar');
  const completionCaption = document.getElementById('completion-caption');
  if (completionPercent) completionPercent.textContent = `${completion}%`;
  if (completionBar) completionBar.style.width = `${completion}%`;
  if (completionCaption) completionCaption.textContent = `${totals.done || 0} of ${total} deliverables complete`;
  const breakdown = document.getElementById('completion-breakdown');
  if (breakdown) breakdown.textContent = `${totals.at_risk || 0} at risk · ${projectDashboard.upcoming_tasks.length} due soon`;

  const meetingsNode = document.getElementById('dashboard-meetings');
  const meetingCount = document.getElementById('meeting-count');
  if (meetingCount) meetingCount.textContent = meetings.length;
  if (meetingsNode) meetingsNode.innerHTML = meetings.length
    ? meetings.slice(0, 3).map(meeting => `<div class="dashboard-list-row"><strong>${escapeHtml(meeting.title)}</strong><span>${formatDate(meeting.created_at)}</span></div>`).join('')
    : '<div class="inline-empty">No project meetings yet.</div>';

  const needsReview = tasks.filter(task => task.status === 'REVIEW');
  const reviewCount = document.getElementById('review-count');
  const reviewList = document.getElementById('needs-review-list');
  if (reviewCount) reviewCount.textContent = needsReview.length;
  if (reviewList) reviewList.innerHTML = needsReview.length
    ? needsReview.slice(0, 3).map(task => `<div class="dashboard-list-row"><strong>${escapeHtml(task.title)}</strong><span>${escapeHtml(task.owner_name || 'Unassigned')}</span></div>`).join('')
    : '<div class="inline-empty">Nothing waiting for review.</div>';

  const deliverables = document.getElementById('deliverables-overview');
  if (deliverables) deliverables.innerHTML = statusCounts.map(([label, count, color]) => `<div class="deliverable-count-row"><span>${label}</span><span class="deliverable-count-track"><i style="width:${total ? Math.max(4, count / total * 100) : 0}%;background:${color}"></i></span><strong>${count}</strong></div>`).join('');

  updateActiveProjectName();
}

function renderTimeline(tasks) {
  const timeline = document.getElementById('task-timeline');
  const totals = document.getElementById('deliverables-totals');
  if (!timeline) return;
  if (totals) totals.textContent = `${tasks.length} tasks · ${tasks.filter(task => task.risk).length} at risk`;
  const dated = tasks.filter(task => task.due_date).sort((left, right) => left.due_date.localeCompare(right.due_date));
  if (!dated.length) {
    timeline.innerHTML = '<div class="inline-empty">No task due dates are scheduled.</div>';
    return;
  }
  const day = 86400000;
  const timestamps = dated.flatMap(task => [
    task.created_at ? new Date(task.created_at).setHours(0, 0, 0, 0) : new Date(task.due_date).getTime(),
    new Date(`${task.due_date}T00:00:00`).getTime(),
  ]);
  const rangeStart = Math.min(...timestamps);
  const rangeEnd = Math.max(...timestamps, rangeStart + 7 * day);
  const rangeDays = Math.max(1, Math.ceil((rangeEnd - rangeStart) / day));
  const markers = Array.from({ length: Math.min(rangeDays + 1, 21) }, (_, index) => {
    const date = new Date(rangeStart + index * day);
    return `<span>${date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}</span>`;
  }).join('');
  timeline.innerHTML = `<div class="gantt-head"><span>Deliverable</span><div class="gantt-dates">${markers}</div></div>` + dated.map(task => {
    const start = task.created_at ? new Date(task.created_at).setHours(0, 0, 0, 0) : new Date(`${task.due_date}T00:00:00`).getTime();
    const end = new Date(`${task.due_date}T00:00:00`).getTime();
    const left = Math.max(0, Math.min(100, (start - rangeStart) / (rangeDays * day) * 100));
    const width = Math.max(3, Math.min(100 - left, (end - start) / (rangeDays * day) * 100));
    return `<div class="gantt-row"><div class="gantt-task-label"><strong>${escapeHtml(task.title)}</strong><span>${escapeHtml(task.owner_name || 'Unassigned')} · ${escapeHtml(task.status.replaceAll('_', ' '))}</span></div><div class="gantt-track"><span class="gantt-bar status-${task.status.toLowerCase()}" style="left:${left}%;width:${width}%" title="Due ${escapeHtml(task.due_date)}"></span></div></div>`;
  }).join('');
}

function renderDocumentsView(documents) {
  const tbody = document.getElementById('panel-documents-tbody');
  if (!tbody) return;
  if (!documents.length) {
    tbody.innerHTML = '<tr><td colspan="6" class="table-empty">No documents found for this project.</td></tr>';
    return;
  }
  renderDocuments(documents, tbody);
}

function renderJiraMetrics(metrics) {
  const values = [
    ['jira-open', metrics.open],
    ['jira-sprint', metrics.in_sprint],
    ['jira-overdue', metrics.overdue],
    ['jira-progress', `${metrics.sprint_progress}%`],
  ];
  values.forEach(([id, value]) => {
    const node = document.getElementById(id);
    if (node) node.textContent = value;
  });
  const bar = document.getElementById('jira-progress-bar');
  if (bar) bar.style.width = `${metrics.sprint_progress}%`;
}

function formatDate(value) {
  if (!value) return 'Date unavailable';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Date unavailable' : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
}

function renderTasks(tasks) {
  const lanes = {
    BACKLOG: 'tasks-backlog',
    IN_PROGRESS: 'tasks-in-progress',
    REVIEW: 'tasks-review',
    DONE: 'tasks-done',
  };
  Object.values(lanes).forEach(id => {
    const lane = document.getElementById(id);
    if (lane) lane.innerHTML = '';
  });
  tasks.forEach(task => {
    const lane = document.getElementById(lanes[task.status]);
    if (!lane) return;
    const canUpdate = activeUser && (['ADMIN', 'MANAGER'].includes(activeUser.role) || task.owner_id === activeUser.id);
    const card = document.createElement('article');
    card.className = 'kanban-task';
    card.innerHTML = `
      <strong>${escapeHtml(task.title)}</strong>
      <div class="kanban-task-meta">${escapeHtml(task.owner_name || 'Unassigned')}${task.due_date ? ` · Due ${escapeHtml(task.due_date)}` : ''}</div>
      ${task.risk ? `<span class="task-risk">At risk: ${escapeHtml(task.risk_reason || 'Needs attention')}</span>` : ''}
      ${(task.source_meeting_id || task.source_document_id) ? `<div class="source-meta"><span class="source-chip">AI found</span>${task.source_document_id ? `<button type="button" class="text-button task-source" data-document-id="${escapeHtml(task.source_document_id)}">Source document</button>` : ''}${task.source_meeting_id ? '<span class="source-chip">Meeting action</span>' : ''}</div>` : ''}
      <select class="input-text task-status-control" data-task-id="${escapeHtml(task.id)}" aria-label="Task status" ${canUpdate ? '' : 'disabled'}>
        <option value="BACKLOG" ${task.status === 'BACKLOG' ? 'selected' : ''}>Backlog</option>
        <option value="IN_PROGRESS" ${task.status === 'IN_PROGRESS' ? 'selected' : ''}>In Progress</option>
        <option value="REVIEW" ${task.status === 'REVIEW' ? 'selected' : ''}>Review</option>
        <option value="DONE" ${task.status === 'DONE' ? 'selected' : ''}>Done</option>
      </select>`;
    card.querySelector('.task-status-control').addEventListener('change', async event => {
      try {
        await Coordin8Api.updateTask(task.id, { status: event.target.value });
        await refreshProjectViews();
        await initDocumentsTable();
      } catch (error) {
        window.alert(error.message);
      }
    });
    card.querySelector('.task-source')?.addEventListener('click', () => window.inspectDocument(task.source_document_id));
    lane.appendChild(card);
  });
}

function renderTaskOwners(members) {
  const select = document.getElementById('task-owner');
  if (!select) return;
  select.innerHTML = '<option value="">Unassigned</option>' + members.map(member =>
    `<option value="${escapeHtml(member.user_id)}">${escapeHtml(member.name)}</option>`
  ).join('');
}

function renderMeetings(meetings, canManage) {
  const container = document.getElementById('meetings-list');
  if (!container) return;
  if (meetings.length === 0) {
    container.innerHTML = '<div class="card-panel">No project meetings yet.</div>';
    return;
  }
  container.innerHTML = meetings.map(meeting => `
    <article class="meeting-record">
      <h3>${escapeHtml(meeting.title)}</h3>
      <div class="meeting-meta">${formatDate(meeting.created_at)}</div>
      ${meeting.summary ? `<p>${escapeHtml(meeting.summary)}</p>` : '<p>Minutes have not been generated.</p>'}
      ${meeting.decisions.length ? `<h4>Decisions</h4><ul>${meeting.decisions.map(item => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : ''}
      ${meeting.action_items.length ? `<h4>Action Items</h4><ul>${meeting.action_items.map(item => {
        const overdue = item.due_date && new Date(`${item.due_date}T00:00:00`) < new Date(new Date().setHours(0, 0, 0, 0));
        return `<li>${escapeHtml(item.text)}${item.owner_label ? ` · ${escapeHtml(item.owner_label)}` : ''}${item.due_date ? ` · ${escapeHtml(item.due_date)}` : ''}${overdue ? ' <span class="task-risk">Overdue</span>' : ''}${item.task_id ? ' · Task created' : ''}${canManage && !item.task_id ? ` <button class="btn btn-secondary action-to-task" data-id="${escapeHtml(item.id)}">Create Task</button>` : ''}</li>`;
      }).join('')}</ul>` : ''}
      ${canManage ? `<div class="meeting-actions"><button class="btn btn-secondary generate-mom" data-id="${escapeHtml(meeting.id)}">${meeting.summary ? 'Regenerate MoM' : 'Generate MoM'}</button></div>` : ''}
    </article>`).join('');
  container.querySelectorAll('.generate-mom').forEach(button => button.addEventListener('click', async () => {
    try {
      await Coordin8Api.generateMom(button.dataset.id);
      await refreshProjectViews();
    } catch (error) {
      window.alert(error.message);
    }
  }));
  container.querySelectorAll('.action-to-task').forEach(button => button.addEventListener('click', async () => {
    try {
      await Coordin8Api.actionItemToTask(button.dataset.id);
      await refreshProjectViews();
      await initDocumentsTable();
    } catch (error) {
      window.alert(error.message);
    }
  }));
}

function renderTeam(members) {
  const tbody = document.getElementById('team-tbody');
  if (!tbody) return;
  tbody.innerHTML = members.map(member =>
    `<tr><td>${escapeHtml(member.name)}</td><td>${escapeHtml(member.role.replaceAll('_', ' '))}</td><td>${member.active_tasks}</td></tr>`
  ).join('');
}

function renderWeeklyReport(report) {
  const container = document.getElementById('weekly-report');
  if (!container) return;
  container.innerHTML = `
    <p>Progress: <strong>${report.progress.completed} of ${report.progress.total} tasks complete</strong> (${report.progress.completion_percentage}%)</p>
    <h3>Risks</h3>
    ${report.risks.length ? `<ul>${report.risks.map(task => `<li>${escapeHtml(task.title)}: ${escapeHtml(task.risk_reason)}</li>`).join('')}</ul>` : '<p>No at-risk tasks.</p>'}
    <h3>Next Steps</h3>
    ${report.next_steps.length ? `<ul>${report.next_steps.map(task => `<li>${escapeHtml(task.title)}${task.due_date ? ` · ${escapeHtml(task.due_date)}` : ''}</li>`).join('')}</ul>` : '<p>No open tasks.</p>'}
    <p>Meetings this week: ${report.meetings_this_week}</p>`;
}

// Navigation Handling
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  const panels = document.querySelectorAll('.view-panel');
  const pageTitle = document.getElementById('current-page-title');

  navItems.forEach(item => {
    if (!item.dataset.navigationBound) item.dataset.navigationBound = 'true';
    else return;
    item.addEventListener('click', () => {
      if (item.hidden) return;
      const targetView = item.getAttribute('data-view');
      navItems.forEach(i => i.classList.remove('active'));
      panels.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const panel = document.getElementById(`panel-${targetView}`);
      if (panel) panel.classList.add('active');

      if (pageTitle) {
        pageTitle.textContent = item.querySelector('span').textContent;
      }
      window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#/${targetView}`);
      if (targetView === 'admin-projects' || targetView === 'admin-employees') loadAdminManagement();
      if (targetView === 'documents' || targetView === 'dashboard' || targetView === 'deliverables' || targetView === 'meetings' || targetView === 'reports' || targetView === 'team' || targetView === 'jira') refreshProjectViews();
    });
  });

  document.querySelectorAll('[data-open-view]').forEach(button => {
    button.addEventListener('click', () => document.querySelector(`[data-view="${button.dataset.openView}"]`)?.click());
  });
}

// Documents Table & Dashboard Metrics
async function initDocumentsTable() {
  if (!Coordin8Api.activeProjectId) {
    setViewState('documents', 'empty', 'Select an accessible project to view documents.');
    return;
  }
  setViewState('documents', 'loading', 'Loading project documents...');
  try {
    const documents = await Coordin8Api.documents();
    renderDocumentsView(documents);
    setViewState('documents', documents.length ? 'clear' : 'empty', 'No documents found for this project.');
  } catch {
    setViewState('documents', 'error', 'Unable to load project documents. Please try again.');
  }
}

function renderDocuments(documents, tbody) {
  tbody.innerHTML = '';
  documents.forEach(doc => {
    const tr = document.createElement('tr');
    const sizeMb = doc.file_size_bytes ? (doc.file_size_bytes / 1024 / 1024).toFixed(2) : '0.00';
    const summary = doc.summary || '—';
    const ftype = (doc.file_type || 'doc').toLowerCase();

    tr.innerHTML = `
      <td><strong>${escapeHtml(doc.title)}</strong><div style="font-size: 11px; color: var(--text-dim);">${doc.document_id}</div></td>
      <td><span class="badge badge-${ftype}">${ftype.toUpperCase()}</span></td>
      <td>${sizeMb} MB</td>
      <td><span class="badge ${(doc.status || '').toUpperCase() === 'READY' ? 'badge-ready' : 'badge-processing'}">${escapeHtml(doc.status || 'REGISTERED')}</span></td>
      <td style="font-size: 12px; color: var(--text-muted); max-width: 340px;">${escapeHtml(summary)}</td>
      <td>
        <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 11px;" onclick="inspectDocument('${escapeHtml(doc.document_id)}')">Source</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

function initProjectChat() {
  const form = document.getElementById('project-chat-form');
  const searchInput = document.getElementById('search-query-input');
  const askBtn = document.getElementById('btn-ask-query');
  const history = document.getElementById('chat-history');
  const attachButton = document.getElementById('chat-attach-button');
  const fileInput = document.getElementById('chat-file-input');
  const uploadStatus = document.getElementById('chat-upload-status');
  if (!form || !searchInput || !askBtn) return;

  history?.addEventListener('click', event => {
    const starter = event.target.closest('[data-chat-starter]');
    if (!starter) return;
    searchInput.value = starter.dataset.chatStarter;
    form.requestSubmit();
  });

  attachButton?.addEventListener('click', () => fileInput?.click());
  fileInput?.addEventListener('change', async () => {
    const file = fileInput.files?.[0];
    fileInput.value = '';
    if (file) await uploadChatDocument(file);
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (chatUploadInProgress) return;
    const query = searchInput.value.trim();
    if (!query) return;
    const projectId = Coordin8Api.activeProjectId;
    if (!projectId) {
      setViewState('chat', 'error', 'Select an accessible project to ask a question.');
      return;
    }

    appendChatMessage('user', query);
    searchInput.value = '';
    searchInput.disabled = true;
    askBtn.disabled = true;
    setViewState('chat', 'clear');
    const thinking = document.createElement('div');
    thinking.className = 'chat-message chat-bot chat-thinking';
    thinking.textContent = 'Coordin8 is thinking...';
    history?.appendChild(thinking);
    if (history) history.scrollTop = history.scrollHeight;

    try {
      const data = await Coordin8Api.chat(query, projectId);
      if (Coordin8Api.activeProjectId !== projectId) return;
      appendChatMessage('bot', data.answer, data.sources?.length ? data.sources : data.citations, data.grounded ?? Boolean(data.citations?.length));
      setViewState('chat', 'clear');
    } catch (error) {
      if (Coordin8Api.activeProjectId !== projectId) return;
      const message = error.status === 403
        ? 'You do not have access to this project.'
        : error.status === 502
          ? (error.message || 'AI service is currently unavailable. Please try again.')
          : error instanceof TypeError
            ? 'Unable to connect to Coordin8. Please try again.'
            : (error.message || 'Unable to connect to Coordin8. Please try again.');
      setViewState('chat', 'error', message);
    }
    finally {
      thinking.remove();
      searchInput.disabled = false;
      askBtn.disabled = false;
      if (Coordin8Api.activeProjectId === projectId) searchInput.focus();
    }
  });

  async function uploadChatDocument(file) {
    const projectId = Coordin8Api.activeProjectId;
    const project = accessibleProjects.find(item => item.id === projectId);
    const projectName = project?.name || 'the selected project';
    if (!uploadStatus) return;
    if (!projectId) {
      uploadStatus.hidden = false;
      uploadStatus.textContent = 'Select an accessible project before uploading a document.';
      return;
    }

    chatUploadInProgress = true;
    uploadStatus.hidden = false;
    uploadStatus.textContent = `${file.name} · Uploading and indexing for ${projectName}...`;
    if (attachButton) attachButton.disabled = true;
    searchInput.disabled = true;
    askBtn.disabled = true;
    const formData = new FormData();
    formData.append('file', file);

    try {
      const document = await Coordin8Api.uploadDocument(formData, projectId);
      if (document.success !== true || String(document.status).toUpperCase() !== 'READY') {
        throw new Error('The ingestion pipeline did not mark the document ready.');
      }
      if (Coordin8Api.activeProjectId !== projectId) return;
      uploadStatus.textContent = `✓ ${file.name} is ready in ${projectName}. You can now ask questions about it.`;
      await initDocumentsTable();
    } catch {
      if (Coordin8Api.activeProjectId === projectId) {
        uploadStatus.textContent = `✕ ${file.name} could not be processed. Please try again.`;
      }
    } finally {
      chatUploadInProgress = false;
      if (attachButton) attachButton.disabled = false;
      searchInput.disabled = false;
      askBtn.disabled = false;
    }
  }
}

function clearProjectChat() {
  const history = document.getElementById('chat-history');
  if (history) history.innerHTML = chatEmptyMarkup();
  const uploadStatus = document.getElementById('chat-upload-status');
  if (uploadStatus) {
    uploadStatus.hidden = true;
    uploadStatus.textContent = '';
  }
  setViewState('chat', 'clear');
}

function chatEmptyMarkup() {
  return `<div class="chat-empty" id="chat-empty">
    <p>Ask about this project's documents, meetings, tasks and updates.</p>
    <div class="chat-starters" aria-label="Starter questions">
      <button type="button" data-chat-starter="What is the current project delivery date?">What is the current project delivery date?</button>
      <button type="button" data-chat-starter="What are the current project risks?">What are the current project risks?</button>
      <button type="button" data-chat-starter="Which tasks are overdue?">Which tasks are overdue?</button>
      <button type="button" data-chat-starter="Summarize the latest meeting.">Summarize the latest meeting.</button>
      <button type="button" data-chat-starter="What are the major project milestones?">What are the major project milestones?</button>
    </div>
  </div>`;
}

function appendChatMessage(sender, text, sources = [], grounded = false) {
  const chatHistory = document.getElementById('chat-history');
  if (!chatHistory) return;
  document.getElementById('chat-empty')?.remove();

  const msgDiv = document.createElement('div');
  msgDiv.className = `chat-message chat-${sender}`;

  let contentHtml = `<div>${text ? escapeHtml(text).replace(/\n/g, '<br/>') : ''}</div>`;
  if (sender === 'bot') {
    contentHtml += `<div class="chat-grounding ${grounded ? 'is-grounded' : ''}">${grounded ? 'Grounded in project knowledge' : 'No project sources were retrieved'}</div>`;
  }
  if (sender === 'bot' && sources?.length) {
    contentHtml += '<div class="chat-sources"><strong>Sources</strong>';
    sources.forEach(source => {
      const title = typeof source === 'string' ? 'Project source' : (source.document_title || 'Project source');
      const citation = typeof source === 'string' ? source : source.citation;
      contentHtml += `<div class="chat-source"><span>📄 ${escapeHtml(title)}</span>${citation ? `<small>${escapeHtml(citation)}</small>` : ''}</div>`;
    });
    contentHtml += '</div>';
  }

  msgDiv.innerHTML = contentHtml;
  chatHistory.appendChild(msgDiv);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Developer Provenance Inspector View (Section 26)
function initInspectorView() {
  const tabQuery = document.getElementById('tab-mode-query');
  const tabDoc = document.getElementById('tab-mode-doc');
  const queryControls = document.getElementById('inspector-query-controls');
  const docControls = document.getElementById('inspector-doc-controls');
  const queryInput = document.getElementById('inspector-query-input');
  const inspectBtn = document.getElementById('btn-inspect-query');
  const exploreDocBtn = document.getElementById('btn-explore-doc');
  const docSelect = document.getElementById('inspector-doc-select');
  const chipBtns = document.querySelectorAll('.inspector-chip-btn');

  // Mode tab switching
  if (tabQuery && tabDoc) {
    tabQuery.addEventListener('click', () => {
      tabQuery.classList.add('active');
      tabDoc.classList.remove('active');
      if (queryControls) queryControls.style.display = 'block';
      if (docControls) docControls.style.display = 'none';
    });

    tabDoc.addEventListener('click', () => {
      tabDoc.classList.add('active');
      tabQuery.classList.remove('active');
      if (queryControls) queryControls.style.display = 'none';
      if (docControls) docControls.style.display = 'block';
      populateDocSelect();
    });
  }

  // Quick chip buttons
  chipBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.getAttribute('data-query');
      if (queryInput) queryInput.value = q;
      inspectQuery(q);
    });
  });

  // Query search button & Enter key
  if (inspectBtn && queryInput) {
    inspectBtn.addEventListener('click', () => {
      const q = queryInput.value.trim();
      if (q) inspectQuery(q);
    });
    queryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const q = queryInput.value.trim();
        if (q) inspectQuery(q);
      }
    });
  }

  // Document explore button
  if (exploreDocBtn && docSelect) {
    exploreDocBtn.addEventListener('click', () => {
      const docId = docSelect.value;
      if (docId) inspectDocumentHierarchy(docId);
    });
  }

  // Initial load
  populateDocSelect().then(() => {
    if (queryInput && !queryInput.value) {
      queryInput.value = 'walmart receipt total';
      inspectQuery('walmart receipt total');
    }
  });
}

async function populateDocSelect() {
  const docSelect = document.getElementById('inspector-doc-select');
  if (!docSelect) return;

  try {
    const docs = await Coordin8Api.documents();
    if (docs.length > 0) {
      docSelect.innerHTML = docs.map(d =>
        `<option value="${d.document_id}">${escapeHtml(d.title)} (${(d.file_type || 'doc').toUpperCase()}) — ${d.document_id}</option>`
      ).join('');
      return;
    } else {
      docSelect.innerHTML = '<option value="">No documents found in knowledge base</option>';
      return;
    }
  } catch (e) {
    console.warn('Failed to load documents for selector:', e);
  }

  docSelect.innerHTML = '<option value="">Backend disconnected</option>';
}

async function inspectQuery(query) {
  const container = document.getElementById('inspector-list');
  const summaryBar = document.getElementById('inspector-summary-bar');
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: 32px; color: var(--text-muted);">
      <div style="font-size: 20px; margin-bottom: 8px;">⏳</div>
      <div>Running hierarchical retrieval pipeline across knowledge base...</div>
      <div style="font-size: 11px; color: var(--text-dim); margin-top: 4px;">Searching document summaries &rarr; candidate sections &rarr; fine chunk scoring &rarr; RRF &rarr; reranking</div>
    </div>
  `;

  try {
    const data = await Coordin8Api.search(query, 10);
    renderQueryInspectionResults(data, container, summaryBar);
    return;
  } catch (err) {
    console.warn('Live search inspection failed:', err);
  }

  // If backend unavailable
  if (summaryBar) summaryBar.style.display = 'none';
  container.innerHTML = `
    <div style="text-align: center; padding: 32px; color: var(--text-muted); background: hsla(0, 84%, 60%, 0.08); border: 1px solid #ef4444; border-radius: var(--radius-sm);">
      <div style="font-size: 16px; font-weight: 600; margin-bottom: 6px; color: #f87171;">⚠️ Backend Search Unavailable</div>
      <div style="font-size: 12px; color: var(--text-main);">${escapeHtml(Coordin8Api.activeProjectId ? 'Project search is currently unavailable.' : 'Select an accessible project to search.')}</div>
    </div>
  `;
}

function renderQueryInspectionResults(data, container, summaryBar) {
  if (summaryBar) {
    summaryBar.style.display = 'flex';
    summaryBar.innerHTML = `
      <div><strong>Query:</strong> "${escapeHtml(data.query)}"</div>
      <div><strong>Parsed Intent:</strong> <code style="color: var(--accent);">${escapeHtml(data.intent || 'information_retrieval')}</code></div>
      <div><strong>Candidate Docs Scanned:</strong> ${data.candidate_documents || 0}</div>
      <div><strong>Ranked Chunks:</strong> ${data.results ? data.results.length : 0}</div>
    `;
  }

  if (!data.results || data.results.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 16px; color: var(--text-muted);">
        <div style="font-size: 16px; font-weight: 500; margin-bottom: 6px;">No chunks matched this query</div>
        <div style="font-size: 12px; color: var(--text-dim);">Try broader keywords or inspect a document directly in the "Document Structure & Chunks" tab.</div>
      </div>
    `;
    return;
  }

  container.innerHTML = '';
  data.results.forEach((r, idx) => {
    const card = document.createElement('div');
    card.className = 'inspector-node';

    const ftype = (r.file_type || 'doc').toLowerCase();
    const locIcon = ftype === 'pdf' ? '📄' : (ftype === 'xlsx' ? '📊' : (ftype === 'pptx' ? '📽️' : (ftype === 'image' ? '🖼️' : '📝')));

    card.innerHTML = `
      <div class="inspector-header">
        <div class="lineage-badge">
          <span>${locIcon}</span>
          <span class="badge badge-${ftype}">${ftype.toUpperCase()}</span>
          <strong>${escapeHtml(r.document_title || r.document_id)}</strong>
          <span class="lineage-arrow">&rarr;</span>
          <span>${escapeHtml(r.section_id)}</span>
          <span class="lineage-arrow">&rarr;</span>
          <code style="color: var(--accent);">${escapeHtml(r.chunk_id)}</code>
        </div>
        <div style="display: flex; gap: 8px; align-items: center;">
          <span class="badge" style="background: hsla(217, 91%, 60%, 0.15); color: var(--accent); border: 1px solid hsla(217, 91%, 60%, 0.3);">
            RRF Rank #${r.fusion_rank || (idx + 1)}
          </span>
          <span class="badge badge-ready">Score: ${r.score}</span>
        </div>
      </div>

      <div class="inspector-content-box">${escapeHtml(r.content)}</div>

      <div class="score-pills-grid">
        <div class="score-pill-item">
          <span>Retriever:</span>
          <span class="score-pill-val">${escapeHtml(r.retriever_type || 'Hybrid')}</span>
        </div>
        <div class="score-pill-item">
          <span>Dense Score:</span>
          <span class="score-pill-val">${r.dense_score !== undefined ? r.dense_score : '0.00'}</span>
        </div>
        <div class="score-pill-item">
          <span>Sparse Score:</span>
          <span class="score-pill-val">${r.sparse_score !== undefined ? r.sparse_score : '0.00'}</span>
        </div>
        <div class="score-pill-item">
          <span>Reranker:</span>
          <span class="score-pill-val">${r.reranker_score !== undefined ? r.reranker_score : r.score}</span>
        </div>
        <div class="score-pill-item" style="flex: 1;">
          <span>Source Provenance:</span>
          <span style="color: var(--accent); font-weight: 500;">🔖 ${escapeHtml(r.provenance || 'Source Evidence')}</span>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

async function inspectDocumentHierarchy(docId) {
  const container = document.getElementById('inspector-list');
  const summaryBar = document.getElementById('inspector-summary-bar');
  if (!container) return;

  container.innerHTML = `
    <div style="text-align: center; padding: 32px; color: var(--text-muted);">
      <div style="font-size: 20px; margin-bottom: 8px;">⏳</div>
      <div>Loading structural hierarchy for document ${escapeHtml(docId)}...</div>
    </div>
  `;

  try {
    const data = await Coordin8Api.hierarchy(docId);
    renderDocumentHierarchyResults(data, container, summaryBar);
    return;
  } catch (err) {
    console.warn('Failed to fetch document hierarchy:', err);
  }

  container.innerHTML = `
    <div style="color: #f87171; padding: 20px; background: hsla(0, 84%, 60%, 0.1); border-radius: var(--radius-sm);">
      Could not load hierarchy for ${escapeHtml(docId)}. Ensure backend is running.
    </div>
  `;
}

function renderDocumentHierarchyResults(data, container, summaryBar) {
  if (summaryBar) {
    summaryBar.style.display = 'flex';
    summaryBar.innerHTML = `
      <div><strong>Document:</strong> ${escapeHtml(data.title)}</div>
      <div><strong>Format:</strong> <span class="badge badge-${data.file_type}">${data.file_type.toUpperCase()}</span></div>
      <div><strong>Status:</strong> <span class="badge badge-ready">${data.status}</span></div>
      <div><strong>Total Sections:</strong> ${data.sections ? data.sections.length : 0}</div>
      <div><strong>Total Chunks:</strong> ${data.total_chunks}</div>
    `;
  }

  container.innerHTML = `
    <div style="background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 16px; margin-bottom: 14px;">
      <div style="font-size: 13px; font-weight: 600; color: var(--text-main); margin-bottom: 4px;">Document-Level Summary:</div>
      <div style="font-size: 13px; color: var(--text-muted); line-height: 1.5;">${escapeHtml(data.summary || 'Summary generated during canonical pipeline.')}</div>
    </div>
  `;

  if (!data.sections || data.sections.length === 0) {
    container.innerHTML += `
      <div style="text-align: center; color: var(--text-dim); padding: 24px;">No chunks or sections extracted for this document.</div>
    `;
    return;
  }

  data.sections.forEach((sec, secIdx) => {
    const secDiv = document.createElement('div');
    secDiv.className = 'inspector-node';
    secDiv.style.borderLeft = '3px solid var(--accent)';

    let chunksHtml = '';
    sec.chunks.forEach((chk, chkIdx) => {
      const locInfo = chk.page ? `Page ${chk.page}` : (chk.slide ? `Slide ${chk.slide}` : (chk.sheet ? `Sheet '${chk.sheet}'` : 'Main Chunk'));
      chunksHtml += `
        <div style="background: var(--bg-primary); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 12px; margin-top: 10px;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 11px; color: var(--text-muted);">
            <div style="display: flex; gap: 8px; align-items: center;">
              <span style="font-weight: 600; color: var(--text-main);">Chunk #${chkIdx + 1}:</span>
              <code>${chk.chunk_id}</code>
              <span class="badge" style="background: hsla(220, 20%, 25%, 0.6);">${chk.content_type || 'text'}</span>
            </div>
            <div>
              <span style="color: var(--accent); font-weight: 500;">📍 ${locInfo}</span> | <span>${chk.token_count || 0} tokens</span>
            </div>
          </div>
          <pre style="margin: 0; font-family: var(--font-mono); font-size: 12px; color: var(--text-main); white-space: pre-wrap; max-height: 160px; overflow-y: auto;">${escapeHtml(chk.content)}</pre>
        </div>
      `;
    });

    secDiv.innerHTML = `
      <div class="inspector-header">
        <div>
          <span style="font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0;">Section ${secIdx + 1}</span>
          <div style="font-size: 14px; font-weight: 600; color: var(--text-main); margin-top: 2px;">${escapeHtml(sec.section_id)}</div>
        </div>
        <span class="badge" style="background: hsla(217, 91%, 60%, 0.15); color: var(--accent); border: 1px solid hsla(217, 91%, 60%, 0.3);">
          ${sec.chunks_count} chunks
        </span>
      </div>
      <div style="margin-top: 8px;">${chunksHtml}</div>
    `;

    container.appendChild(secDiv);
  });
}


// Real Ingestion & Upload Handling
function initUpload() {
  const dropzone = document.getElementById('file-dropzone');
  const fileInput = document.getElementById('file-input');
  const statusDiv = document.getElementById('upload-status');

  if (!dropzone || !fileInput) return;

  dropzone.addEventListener('click', event => {
    if (event.target !== fileInput) fileInput.click();
  });

  // Prevent default drag behaviors on window and dropzone
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    window.addEventListener(eventName, (e) => e.preventDefault(), false);
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
    }, false);
  });

  // Drag visual effects
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
      dropzone.style.borderColor = 'var(--accent)';
      dropzone.style.background = 'hsla(217, 91%, 60%, 0.08)';
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => {
      dropzone.style.borderColor = 'var(--border-subtle)';
      dropzone.style.background = 'var(--bg-primary)';
    });
  });

  // File Drop
  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      uploadFile(dt.files[0]);
    }
  });

  // File Input change
  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
      fileInput.value = ''; // Reset
    }
  });

  async function uploadFile(file) {
    if (!statusDiv) return;

    statusDiv.hidden = false;
    statusDiv.textContent = `Uploading ${file.name}...`;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const doc = await Coordin8Api.uploadDocument(formData);
      const status = doc.status || (doc.success ? 'READY' : 'REGISTERED');
      statusDiv.innerHTML = `<strong>${escapeHtml(file.name)}</strong> · <span class="badge ${status === 'READY' ? 'badge-ready' : 'badge-processing'}">${escapeHtml(status)}</span>${doc.summary ? `<p>${escapeHtml(doc.summary)}</p>` : ''}`;
      await refreshProjectViews();
    } catch (error) {
      statusDiv.textContent = error.message || 'Upload failed. Please try again.';
    }
  }
}

// Server Health Check
async function checkServerStatus() {
  const indicator = document.getElementById('server-indicator');
  const label = document.getElementById('server-label');
  try {
    await Coordin8Api.health();
    if (indicator) indicator.style.background = 'var(--success)';
    if (label) label.textContent = 'API Connected (8000)';
  } catch {
    if (indicator) indicator.style.background = 'var(--warning)';
    if (label) label.textContent = 'Backend Unavailable';
  }
}

window.inspectDocument = async function(docId) {
  const panel = document.getElementById('document-source-panel');
  const title = document.getElementById('document-source-title');
  const content = document.getElementById('document-source-content');
  if (!panel || !content) return;
  panel.hidden = false;
  if (title) title.textContent = 'Document source';
  content.textContent = 'Loading source details...';
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
  try {
    const document = await Coordin8Api.hierarchy(docId);
    if (title) title.textContent = document.title;
    content.innerHTML = `<p class="muted-copy">${escapeHtml(document.summary || 'No summary available.')}</p><p class="source-meta">${escapeHtml(document.file_type)} · ${escapeHtml(document.status)} · ${document.total_chunks} chunks</p>${document.sections.map(section => `<details class="source-section"><summary>${escapeHtml(section.section_id)} · ${section.chunks_count} chunks</summary>${section.chunks.map(chunk => `<pre>${escapeHtml(chunk.content)}</pre>`).join('')}</details>`).join('')}`;
  } catch (error) {
    content.textContent = error.message || 'Unable to load document source.';
  }
};

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('close-document-source')?.addEventListener('click', () => {
    document.getElementById('document-source-panel').hidden = true;
  });
});

