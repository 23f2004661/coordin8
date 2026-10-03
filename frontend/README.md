# Coordin8 Project Workspace

The frontend is a static HTML/CSS/JavaScript application. It uses the authenticated project API and does not depend on Vue or a frontend build step.

## Run

Start the backend from `backend/`, then serve this directory:

```powershell
python -m http.server 3000
```

Open `http://localhost:3000`. Sign in with an account created by an administrator or the local development seed. The authenticated user and role come from `/api/auth/me`; authorized projects come from `/api/projects`. Project chat, tasks, meetings, documents, reports, team, and Jira requests use the selected project.

The API base defaults to the frontend host on port `8000` with the `/api` prefix. For another backend host, set the `coordin8-api-base` meta tag in `index.html` to the full API base URL, for example `https://api.example.com/api`.

## Screens

- Dashboard with task status, completion, meeting, review, and risk summaries
- Deliverables Kanban and task due-date timeline
- Project meetings, MoM generation, and action-item conversion
- Project documents and citation-backed project chat
- Weekly reports, team members, and demo/mock Jira metrics
- Tenant-admin employee, project, and membership management

Navigation visibility follows the authenticated role for usability. Backend authorization remains authoritative for every protected operation.