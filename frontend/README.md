# Co-ordin8 — Frontend (Vue.js + Bootstrap)

An AI project manager for professional services (accounting, consulting, legal) — frontend-only demo, built with **Vue 3** and **Bootstrap 5**.

This is a static prototype: all data in `js/app.js` is mocked in-browser. There is no backend yet — it's meant to be wired up to the FastAPI + RAG + MCP backend described in the project proposal.

## Structure

```
.
├── index.html      # Page markup + Vue app mount point
├── css/
│   └── style.css   # All custom styling (design tokens, layout, components)
├── js/
│   └── app.js       # Vue app: state, mock data, computed properties, chart rendering
└── README.md
```

## Stack

- **Vue 3** (loaded via CDN, no build step)
- **Bootstrap 5** (CDN, used for base grid/utility resets)
- **Chart.js** (CDN) — powers the dashboard's donut and line charts
- Google Fonts — Inter (UI text) and Material Symbols (icons)

No React, no bundler, no npm install required — open `index.html` directly in a browser, or serve the folder with any static file host (GitHub Pages works out of the box).

## Running locally

Just open `index.html` in a browser, or, for a local server:

```bash
npx serve .
# or
python3 -m http.server
```

## What's implemented

- Landing page, login, and signup flows
- Role-based access: Super Admin → Tenant Admin → Project Workspace (Manager / Team member views)
- Multi-project switching
- Deliverables board (Kanban + Gantt timeline)
- Audit trail / source citation on every task
- Deadline risk flagging
- Minutes of Meeting (MoM), document summarization, weekly status reports (mocked)
- Jira metrics panel
- Chat with the project (canned responses over mock data)

## Next steps for the real build

- Replace the mock data objects in `js/app.js` with calls to the FastAPI backend
- Replace the mock `summarizeDoc()` and `sendChat()` functions with real RAG/agent API calls
- Real authentication in place of the login role-picker
