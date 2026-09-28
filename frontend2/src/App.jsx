import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import HomeView from './components/HomeView';
import ProjectDetailView from './components/ProjectDetailView';
import DocumentModal from './components/DocumentModal';
import NewProjectModal from './components/NewProjectModal';
import NewMeetingModal from './components/NewMeetingModal';
import NewDeliverableModal from './components/NewDeliverableModal';
import { INITIAL_PROJECTS } from './data/initialData';
import {
  fetchBackendDocuments,
  fetchProjectsFromBackend,
  createProjectOnBackend,
  rescanProjectOnBackend,
} from './api';

const STORAGE_KEY = 'coordin8_workspace_projects_v2';

export default function App() {
  const [projects, setProjects] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : INITIAL_PROJECTS;
    } catch (e) {
      return INITIAL_PROJECTS;
    }
  });

  const [activeProjectId, setActiveProjectId] = useState(null);
  const [backendDocs, setBackendDocs] = useState([]);
  const [isBackendConnected, setIsBackendConnected] = useState(false);

  // Modals state
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [isNewProjectModalOpen, setIsNewProjectModalOpen] = useState(false);
  const [isNewMeetingModalOpen, setIsNewMeetingModalOpen] = useState(false);
  const [isNewDeliverableModalOpen, setIsNewDeliverableModalOpen] = useState(false);

  // Sync projects to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
    } catch (err) {
      console.warn('Could not save to localStorage:', err);
    }
  }, [projects]);

  // Load projects and documents from backend
  const loadFromBackend = async () => {
    const backendProjects = await fetchProjectsFromBackend();
    if (backendProjects !== null) {
      setIsBackendConnected(true);
      if (backendProjects.length > 0) {
        // Merge backend projects (which have real folders & physical files)
        setProjects((prev) => {
          const merged = [...backendProjects];
          // Preserve any seed projects if not already present
          for (const p of prev) {
            if (!merged.some((m) => m.id === p.id || m.project_id === p.id)) {
              merged.push(p);
            }
          }
          return merged;
        });
      }
    }

    const docs = await fetchBackendDocuments();
    setBackendDocs(docs || []);
  };

  useEffect(() => {
    loadFromBackend();
    const interval = setInterval(loadFromBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  const activeProject =
    projects.find((p) => (p.id || p.project_id) === activeProjectId) || null;

  // Flatten all meetings across all projects
  const allMeetings = projects
    .flatMap((p) =>
      (p.meetings || []).map((m) => ({
        ...m,
        projectId: p.id || p.project_id,
        projectName: p.name,
        projectColor: p.color,
      }))
    )
    .sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime());

  // Flatten all deliverables across all projects
  const allDeliverables = projects
    .flatMap((p) =>
      (p.deliverables || []).map((d) => ({
        ...d,
        projectId: p.id || p.project_id,
        projectName: p.name,
        projectColor: p.color,
      }))
    )
    .sort((a, b) => new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime());

  // Add project handler (calls backend to create folder and dedicated KB)
  const handleAddProject = async (payload) => {
    try {
      // 1. Try creating on FastAPI backend
      const createdOnBackend = await createProjectOnBackend(payload);
      const normalizedProj = {
        ...createdOnBackend,
        id: createdOnBackend.project_id || createdOnBackend.id,
      };
      setProjects((prev) => [normalizedProj, ...prev]);
      setActiveProjectId(normalizedProj.id);
      return normalizedProj;
    } catch (err) {
      console.warn('Backend project creation failed, creating local fallback:', err.message);
      // Fallback local representation
      const newProj = {
        id: `proj_${Date.now()}`,
        name: payload.name,
        code: payload.code,
        description: payload.description,
        category: payload.category,
        color: payload.color,
        folder_path: payload.folder_path || `C:\\Users\\ssrin\\Desktop\\Coordin8 Home\\${payload.name}`,
        progress: 0,
        createdAt: new Date().toISOString().split('T')[0],
        folders: [
          {
            id: 'f_general',
            name: 'General Documents',
            files: [],
          },
        ],
        meetings: [],
        deliverables: [],
      };
      setProjects((prev) => [newProj, ...prev]);
      setActiveProjectId(newProj.id);
      return newProj;
    }
  };

  // Rescan project folder
  const handleRescanProject = async (projectId) => {
    try {
      await rescanProjectOnBackend(projectId);
      await loadFromBackend();
    } catch (err) {
      console.warn('Rescan failed:', err);
    }
  };

  // Add meeting handler
  const handleAddMeeting = (newMeeting) => {
    setProjects((prev) =>
      prev.map((proj) => {
        const pId = proj.id || proj.project_id;
        if (pId === newMeeting.projectId) {
          return {
            ...proj,
            meetings: [newMeeting, ...(proj.meetings || [])],
          };
        }
        return proj;
      })
    );
  };

  // Add deliverable handler
  const handleAddDeliverable = (newDel) => {
    setProjects((prev) =>
      prev.map((proj) => {
        const pId = proj.id || proj.project_id;
        if (pId === newDel.projectId) {
          return {
            ...proj,
            deliverables: [newDel, ...(proj.deliverables || [])],
          };
        }
        return proj;
      })
    );
  };

  // Toggle deliverable status
  const handleToggleDeliverableStatus = (delId) => {
    setProjects((prev) =>
      prev.map((proj) => ({
        ...proj,
        deliverables: (proj.deliverables || []).map((d) => {
          if (d.id === delId) {
            const nextStatus = d.status === 'completed' ? 'in_progress' : 'completed';
            return {
              ...d,
              status: nextStatus,
              progress: nextStatus === 'completed' ? 100 : Math.min(d.progress || 50, 90),
            };
          }
          return d;
        }),
      }))
    );
  };

  // Add file to project folder
  const handleAddFileToProject = (projId, fileObj, folderId) => {
    setProjects((prev) =>
      prev.map((proj) => {
        const pId = proj.id || proj.project_id;
        if (pId !== projId) return proj;
        const updatedFolders = (proj.folders || []).map((f) => {
          if (f.id === folderId || (!folderId && f === proj.folders[0])) {
            return {
              ...f,
              files: [fileObj, ...(f.files || [])],
            };
          }
          return f;
        });
        return {
          ...proj,
          folders: updatedFolders,
        };
      })
    );
  };

  // Open prep document from meeting
  const handleSelectPrepDoc = (docName) => {
    for (const proj of projects) {
      for (const folder of proj.folders || []) {
        const found = (folder.files || []).find((f) => f.name === docName);
        if (found) {
          setSelectedDoc(found);
          return;
        }
      }
    }
    setSelectedDoc({
      id: 'doc_ref',
      name: docName,
      type: docName.split('.').pop(),
      size: 'Cached',
      status: 'READY',
      summary: `Document linked as meeting preparation context for ${docName}.`,
    });
  };

  return (
    <div className="app-container">
      <Navbar
        activeProject={activeProject}
        onSelectProject={(p) => setActiveProjectId(p ? p.id || p.project_id : null)}
        onOpenNewProjectModal={() => setIsNewProjectModalOpen(true)}
      />

      <main className="main-content">
        {!activeProject ? (
          <HomeView
            projects={projects}
            allMeetings={allMeetings}
            allDeliverables={allDeliverables}
            onSelectProject={(p) => setActiveProjectId(p.id || p.project_id)}
            onOpenNewProjectModal={() => setIsNewProjectModalOpen(true)}
            onOpenNewMeetingModal={() => setIsNewMeetingModalOpen(true)}
            onOpenNewDeliverableModal={() => setIsNewDeliverableModalOpen(true)}
            onToggleDeliverableStatus={handleToggleDeliverableStatus}
            onSelectPrepDoc={handleSelectPrepDoc}
          />
        ) : (
          <ProjectDetailView
            project={activeProject}
            backendDocs={backendDocs}
            onBack={() => setActiveProjectId(null)}
            onSelectDoc={setSelectedDoc}
            onAddFileToProject={handleAddFileToProject}
            onRescanProject={handleRescanProject}
            onOpenNewMeetingModal={() => setIsNewMeetingModalOpen(true)}
            onOpenNewDeliverableModal={() => setIsNewDeliverableModalOpen(true)}
            onToggleDeliverableStatus={handleToggleDeliverableStatus}
            onSelectPrepDoc={handleSelectPrepDoc}
          />
        )}
      </main>

      {/* Global Modals */}
      <DocumentModal doc={selectedDoc} onClose={() => setSelectedDoc(null)} />

      <NewProjectModal
        isOpen={isNewProjectModalOpen}
        onClose={() => setIsNewProjectModalOpen(false)}
        onAddProject={handleAddProject}
      />

      <NewMeetingModal
        isOpen={isNewMeetingModalOpen}
        onClose={() => setIsNewMeetingModalOpen(false)}
        projects={projects}
        activeProject={activeProject}
        onAddMeeting={handleAddMeeting}
      />

      <NewDeliverableModal
        isOpen={isNewDeliverableModalOpen}
        onClose={() => setIsNewDeliverableModalOpen(false)}
        projects={projects}
        activeProject={activeProject}
        onAddDeliverable={handleAddDeliverable}
      />
    </div>
  );
}
