import React, { useState, useEffect, useMemo } from 'react';
import Navbar from './components/Navbar';
import HomeView from './components/HomeView';
import ProjectDetailView from './components/ProjectDetailView';
import DocumentModal from './components/DocumentModal';
import NewProjectModal from './components/NewProjectModal';
import NewMeetingModal from './components/NewMeetingModal';
import NewDeliverableModal from './components/NewDeliverableModal';
import GoogleCalendarModal from './components/GoogleCalendarModal';
import { INITIAL_PROJECTS } from './data/initialData';
import { getSavedSession, saveSession, clearSession, fetchCalendarEventsWithToken } from './services/googleCalendar';
import {
  fetchBackendDocuments,
  fetchProjectsFromBackend,
  createProjectOnBackend,
  rescanProjectOnBackend,
  addProjectMeeting,
  batchAddProjectMeetings,
  deleteProjectMeeting,
  addUnassignedMeeting,
  batchAddUnassignedMeetings,
  deleteUnassignedMeeting,
  fetchGcalAccount,
} from './api';

const STORAGE_KEY = 'coordin8_workspace_projects_v3';
const STORAGE_UNASSIGNED_KEY = 'coordin8_workspace_unassigned_v3';

export default function App() {
  const [projects, setProjects] = useState(() => {
    try {
      localStorage.removeItem('coordin8_workspace_projects_v2');
      localStorage.removeItem('coordin8_workspace_projects');
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          const globalSeen = new Set();
          return parsed
            .filter(
              (p) =>
                !['proj_rag_core', 'proj_openworker', 'proj_frontend'].includes(
                  p.id || p.project_id
                )
            )
            .map((p) => {
              const uniqueMeetings = [];
              for (const m of (p.meetings || [])) {
                if (
                  String(m.id || '').startsWith('sim_') ||
                  String(m.id || '').startsWith('gcal_sim_') ||
                  String(m.gcalId || '').startsWith('sim_') ||
                  String(m.gcalId || '').startsWith('gcal_sim_')
                ) continue;
                const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
                if (key && !globalSeen.has(key)) {
                  globalSeen.add(key);
                  uniqueMeetings.push(m);
                }
              }
              return {
                ...p,
                meetings: uniqueMeetings,
              };
            });
        }
      }
      return INITIAL_PROJECTS;
    } catch (e) {
      return INITIAL_PROJECTS;
    }
  });

  const [unassignedMeetings, setUnassignedMeetings] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_UNASSIGNED_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          return parsed.filter(
            (m) =>
              !String(m.id || '').startsWith('sim_') &&
              !String(m.id || '').startsWith('gcal_sim_') &&
              !String(m.gcalId || '').startsWith('sim_') &&
              !String(m.gcalId || '').startsWith('gcal_sim_')
          );
        }
      }
      return [];
    } catch {
      return [];
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
  const [isGoogleCalendarModalOpen, setIsGoogleCalendarModalOpen] = useState(false);
  const [gcalSession, setGcalSession] = useState(getSavedSession());

  // Sync projects and unassigned meetings to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
    } catch (err) {
      console.warn('Could not save to localStorage:', err);
    }
  }, [projects]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_UNASSIGNED_KEY, JSON.stringify(unassignedMeetings));
    } catch (err) {
      console.warn('Could not save unassigned meetings to localStorage:', err);
    }
  }, [unassignedMeetings]);

  // Load projects and documents from backend
  const loadFromBackend = async () => {
    const res = await fetchProjectsFromBackend();
    if (res !== null) {
      setIsBackendConnected(true);

      const normalizedBackend = (res.projects || []).map((bp) => ({
        ...bp,
        id: bp.project_id || bp.id,
      }));

      const backendUnassigned = (res.unassigned_meetings || []).filter(
        (m) =>
          !String(m.id || '').startsWith('sim_') &&
          !String(m.id || '').startsWith('gcal_sim_') &&
          !String(m.gcalId || '').startsWith('sim_') &&
          !String(m.gcalId || '').startsWith('gcal_sim_')
      );

      // 1. Gather all project meetings across backend projects, deduplicated globally
      const projectMeetingKeys = new Set();
      const cleanProjects = normalizedBackend.map((bp) => {
        const cleanMeetings = (bp.meetings || []).filter(
          (m) =>
            !String(m.id || '').startsWith('sim_') &&
            !String(m.id || '').startsWith('gcal_sim_') &&
            !String(m.gcalId || '').startsWith('sim_') &&
            !String(m.gcalId || '').startsWith('gcal_sim_')
        );
        const dedupedMeetings = [];
        for (const m of cleanMeetings) {
          const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
          if (key && !projectMeetingKeys.has(key)) {
            projectMeetingKeys.add(key);
            dedupedMeetings.push(m);
          }
        }
        return {
          ...bp,
          meetings: dedupedMeetings,
        };
      });

      // 2. Gather unassigned meetings, ensuring none are duplicates of project meetings or within unassigned
      const unassignedKeys = new Set();
      const cleanUnassigned = [];
      for (const m of backendUnassigned) {
        const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
        if (key && !projectMeetingKeys.has(key) && !unassignedKeys.has(key)) {
          unassignedKeys.add(key);
          cleanUnassigned.push({
            ...m,
            projectId: null,
            projectName: 'Unassigned',
            projectColor: '#94a3b8',
          });
        }
      }

      // 3. Update state cleanly and purely
      setProjects((prev) => {
        const backendIds = new Set(cleanProjects.map((bp) => bp.id));
        const localCreated = prev.filter(
          (p) =>
            !backendIds.has(p.id || p.project_id) &&
            !['proj_rag_core', 'proj_openworker', 'proj_frontend'].includes(p.id || p.project_id)
        );
        const merged = cleanProjects.map((bp) => {
          const existing = prev.find((p) => (p.id || p.project_id) === bp.id);
          return {
            ...bp,
            deliverables:
              existing?.deliverables && existing.deliverables.length > 0
                ? existing.deliverables
                : bp.deliverables || [],
          };
        });
        return [...merged, ...localCreated];
      });

      setUnassignedMeetings((prevUnassigned) => {
        // Start with cleanUnassigned from backend
        const result = [...cleanUnassigned];
        const existingKeys = new Set(
          cleanUnassigned.map((m) => m.gcalId || m.id || `${m.title}_${m.startTime}`)
        );
        // Retain any locally added unassigned meetings from current session not yet on backend
        for (const m of prevUnassigned) {
          const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
          if (key && !existingKeys.has(key) && !projectMeetingKeys.has(key)) {
            existingKeys.add(key);
            result.push(m);
          }
        }
        return result;
      });
    }

    const docs = await fetchBackendDocuments();
    setBackendDocs(docs || []);
  };

  useEffect(() => {
    loadFromBackend();
    const interval = setInterval(loadFromBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  // Synchronize Google Calendar account session from backend database
  useEffect(() => {
    const syncGcalWithBackend = async () => {
      try {
        const backendAcc = await fetchGcalAccount();
        const saved = getSavedSession();

        if (backendAcc && backendAcc.connected && backendAcc.email) {
          const syncedSession = {
            ...(saved || {}),
            connected: true,
            mode: backendAcc.mode || 'real',
            user: {
              ...(saved?.user || {}),
              email: backendAcc.email,
              name: backendAcc.name || backendAcc.email.split('@')[0],
              picture: backendAcc.picture || saved?.user?.picture || '',
            },
            lastSync: backendAcc.lastSync || saved?.lastSync || new Date().toISOString(),
            syncedCount: backendAcc.syncedCount ?? saved?.syncedCount ?? 0,
          };
          saveSession(syncedSession);
          setGcalSession(syncedSession);
        } else if (saved?.connected) {
          setGcalSession(saved);
        }
      } catch (err) {
        console.debug('Could not sync gcal session with backend:', err);
        const saved = getSavedSession();
        if (saved?.connected) setGcalSession(saved);
      }
    };
    syncGcalWithBackend();
  }, []);

  // Automatic Google Calendar Background Sync Loop (Interval + Window Focus)
  useEffect(() => {
    if (!gcalSession?.connected) return;

    let isAutoSyncing = false;
    const triggerAutoSync = async () => {
      if (isAutoSyncing) return;
      isAutoSyncing = true;
      try {
        if (gcalSession.mode === 'real' && gcalSession.accessToken) {
          const events = await fetchCalendarEventsWithToken(
            gcalSession.accessToken,
            null,
            projects
          );
          if (events && events.length > 0) {
            handleSyncGoogleMeetings(events, {
              ...gcalSession,
              lastSync: new Date().toISOString(),
              syncedCount: events.length,
            });
          }
        }
      } catch (err) {
        console.debug('Background GCal auto-sync notice:', err.message);
      } finally {
        isAutoSyncing = false;
      }
    };

    // 1. Initial sync on startup/mount
    triggerAutoSync();

    // 2. Periodic background polling every 45 seconds
    const calInterval = setInterval(triggerAutoSync, 45000);

    // 3. Instant auto-sync whenever user returns to the Coordin8 browser tab
    const handleVisibilityOrFocus = () => {
      if (document.visibilityState === 'visible') {
        triggerAutoSync();
      }
    };
    document.addEventListener('visibilitychange', handleVisibilityOrFocus);
    window.addEventListener('focus', handleVisibilityOrFocus);

    return () => {
      clearInterval(calInterval);
      document.removeEventListener('visibilitychange', handleVisibilityOrFocus);
      window.removeEventListener('focus', handleVisibilityOrFocus);
    };
  }, [gcalSession?.connected, gcalSession?.accessToken, projects.length]);

  const activeProject =
    projects.find((p) => (p.id || p.project_id) === activeProjectId) || null;

  // Combined and deduplicated meetings across all projects and unassigned pool
  const allMeetings = useMemo(() => {
    const seen = new Set();
    const result = [];

    for (const p of projects) {
      for (const m of (p.meetings || [])) {
        if (
          String(m.id || '').startsWith('sim_') ||
          String(m.id || '').startsWith('gcal_sim_') ||
          String(m.gcalId || '').startsWith('sim_') ||
          String(m.gcalId || '').startsWith('gcal_sim_')
        ) continue;
        const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
        if (key && !seen.has(key)) {
          seen.add(key);
          result.push({
            ...m,
            projectId: p.id || p.project_id,
            projectName: p.name,
            projectColor: p.color,
          });
        }
      }
    }

    for (const m of unassignedMeetings) {
      if (
        String(m.id || '').startsWith('sim_') ||
        String(m.id || '').startsWith('gcal_sim_') ||
        String(m.gcalId || '').startsWith('sim_') ||
        String(m.gcalId || '').startsWith('gcal_sim_')
      ) continue;
      const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
      if (key && !seen.has(key)) {
        seen.add(key);
        result.push({
          ...m,
          projectId: null,
          projectName: 'Unassigned',
          projectColor: '#94a3b8',
        });
      }
    }

    return result.sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime());
  }, [projects, unassignedMeetings]);

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

  // Add meeting handler (leaves unassigned if projectId is empty or not specified)
  const handleAddMeeting = (newMeeting) => {
    const isUnassigned = !newMeeting.projectId || String(newMeeting.projectId).toLowerCase() === 'unassigned';

    if (isUnassigned) {
      const unassignedObj = {
        ...newMeeting,
        projectId: null,
        projectName: 'Unassigned',
        projectColor: '#94a3b8',
      };
      setUnassignedMeetings((prev) => [
        unassignedObj,
        ...prev.filter((m) => (m.id || m.gcalId) !== (newMeeting.id || newMeeting.gcalId)),
      ]);
      setProjects((prev) =>
        prev.map((p) => ({
          ...p,
          meetings: (p.meetings || []).filter(
            (m) => (m.id || m.gcalId) !== (newMeeting.id || newMeeting.gcalId)
          ),
        }))
      );
      addUnassignedMeeting(unassignedObj);
    } else {
      setProjects((prev) =>
        prev.map((proj) => {
          const pId = proj.id || proj.project_id;
          if (pId === newMeeting.projectId) {
            return {
              ...proj,
              meetings: [
                newMeeting,
                ...(proj.meetings || []).filter(
                  (m) => (m.id || m.gcalId) !== (newMeeting.id || newMeeting.gcalId)
                ),
              ],
            };
          }
          return {
            ...proj,
            meetings: (proj.meetings || []).filter(
              (m) => (m.id || m.gcalId) !== (newMeeting.id || newMeeting.gcalId)
            ),
          };
        })
      );
      setUnassignedMeetings((prev) =>
        prev.filter((m) => (m.id || m.gcalId) !== (newMeeting.id || newMeeting.gcalId))
      );
      addProjectMeeting(newMeeting.projectId, newMeeting);
    }
  };

  // Google Calendar sync handler:
  // - Preserves existing project assignments for meetings already assigned.
  // - Leaves brand new meetings unassigned by default.
  // - Eliminates cross-project and unassigned duplicates completely.
  const handleSyncGoogleMeetings = (syncedMeetings, session) => {
    setGcalSession(session);
    if (!syncedMeetings || syncedMeetings.length === 0) return;

    const cleanSynced = syncedMeetings.filter(
      (m) =>
        !String(m.id || '').startsWith('sim_') &&
        !String(m.id || '').startsWith('gcal_sim_') &&
        !String(m.gcalId || '').startsWith('sim_') &&
        !String(m.gcalId || '').startsWith('gcal_sim_')
    );
    if (cleanSynced.length === 0) return;

    setProjects((prevProjects) => {
      const updatedProjects = prevProjects.map((proj) => {
        const existingMeetings = proj.meetings || [];

        const updatedList = existingMeetings.map((em) => {
          const match = cleanSynced.find(
            (sm) =>
              (sm.gcalId && sm.gcalId === em.gcalId) ||
              (sm.id && sm.id === em.id) ||
              (sm.title === em.title && sm.startTime === em.startTime)
          );
          if (match) {
            return {
              ...em,
              title: match.title,
              startTime: match.startTime,
              endTime: match.endTime,
              meetUrl: match.meetUrl,
              attendees: match.attendees,
              agenda: match.agenda,
              isGcal: true,
              gcalId: match.gcalId || em.gcalId,
            };
          }
          return em;
        });

        return {
          ...proj,
          meetings: updatedList,
        };
      });

      // Update unassigned meetings directly using updatedProjects (pure and deterministic)
      setUnassignedMeetings((prevUnassigned) => {
        const allProjectKeys = new Set();
        updatedProjects.forEach((p) => {
          (p.meetings || []).forEach((m) => {
            const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
            if (key) allProjectKeys.add(key);
          });
        });

        const unassignedMap = new Map();

        // 1. Existing unassigned meetings not claimed by any project
        for (const um of prevUnassigned) {
          const key = um.gcalId || um.id || `${um.title}_${um.startTime}`;
          if (key && !allProjectKeys.has(key)) {
            const match = cleanSynced.find(
              (sm) =>
                (sm.gcalId && sm.gcalId === um.gcalId) ||
                (sm.id && sm.id === um.id) ||
                (sm.title === um.title && sm.startTime === um.startTime)
            );
            if (match) {
              unassignedMap.set(key, {
                ...um,
                title: match.title,
                startTime: match.startTime,
                endTime: match.endTime,
                meetUrl: match.meetUrl,
                attendees: match.attendees,
                agenda: match.agenda,
                isGcal: true,
                gcalId: match.gcalId || um.gcalId,
                projectId: null,
                projectName: 'Unassigned',
                projectColor: '#94a3b8',
              });
            } else {
              unassignedMap.set(key, um);
            }
          }
        }

        // 2. Newly synced meetings not claimed by any project or already in unassigned
        for (const sm of cleanSynced) {
          const key = sm.gcalId || sm.id || `${sm.title}_${sm.startTime}`;
          if (key && !allProjectKeys.has(key) && !unassignedMap.has(key)) {
            unassignedMap.set(key, {
              ...sm,
              projectId: null,
              projectName: 'Unassigned',
              projectColor: '#94a3b8',
            });
          }
        }

        const finalUnassigned = Array.from(unassignedMap.values());
        return finalUnassigned;
      });

      return updatedProjects;
    });

    // 3. Persist unassigned meetings to backend outside state updaters
    setProjects((currProjects) => {
      const allProjectKeys = new Set();
      currProjects.forEach((p) => {
        (p.meetings || []).forEach((m) => {
          const key = m.gcalId || m.id || `${m.title}_${m.startTime}`;
          if (key) allProjectKeys.add(key);
        });
      });
      const unassignedToSave = cleanSynced
        .filter((sm) => {
          const key = sm.gcalId || sm.id || `${sm.title}_${sm.startTime}`;
          return key && !allProjectKeys.has(key);
        })
        .map((sm) => ({
          ...sm,
          projectId: null,
          projectName: 'Unassigned',
          projectColor: '#94a3b8',
        }));
      if (unassignedToSave.length > 0) {
        batchAddUnassignedMeetings(unassignedToSave);
      }
      return currProjects;
    });
  };

  // Google Calendar disconnect handler
  const handleDisconnectGcal = () => {
    setGcalSession(null);
  };

  // Reassign single or multiple meetings to a specific project or unassigned
  const handleAssignMeetingsToProject = (meetingIds, targetProjectId) => {
    if (!meetingIds || meetingIds.length === 0) return;
    const isUnassigning = !targetProjectId || String(targetProjectId).toLowerCase() === 'unassigned';

    // Find all matching meetings across all projects and unassigned
    const movingMeetings = [];
    projects.forEach((p) => {
      (p.meetings || []).forEach((m) => {
        const mId = m.id || m.gcalId;
        if (meetingIds.includes(mId)) {
          movingMeetings.push(m);
        }
      });
    });
    unassignedMeetings.forEach((m) => {
      const mId = m.id || m.gcalId;
      if (meetingIds.includes(mId)) {
        movingMeetings.push(m);
      }
    });

    if (movingMeetings.length === 0) return;

    if (isUnassigning) {
      const normalizedForUnassigned = movingMeetings.map((m) => ({
        ...m,
        projectId: null,
        projectName: 'Unassigned',
        projectColor: '#94a3b8',
      }));

      // 1. Remove from all projects in UI
      setProjects((prev) =>
        prev.map((p) => ({
          ...p,
          meetings: (p.meetings || []).filter(
            (m) => !meetingIds.includes(m.id || m.gcalId)
          ),
        }))
      );

      // 2. Add to unassigned in UI (deduped)
      setUnassignedMeetings((prev) => {
        const existingIds = new Set(prev.map((m) => m.id || m.gcalId));
        const newToAdd = normalizedForUnassigned.filter(
          (m) => !existingIds.has(m.id || m.gcalId)
        );
        return [...newToAdd, ...prev];
      });

      // 3. Persist to backend
      batchAddUnassignedMeetings(normalizedForUnassigned);
    } else {
      const targetProj = projects.find(
        (p) => (p.id || p.project_id) === targetProjectId
      );
      if (!targetProj) return;
      const tId = targetProj.id || targetProj.project_id;

      const updatedMoving = movingMeetings.map((m) => ({
        ...m,
        projectId: tId,
        projectName: targetProj.name,
        projectColor: targetProj.color,
      }));

      // 1. Remove from unassigned in UI
      setUnassignedMeetings((prev) =>
        prev.filter((m) => !meetingIds.includes(m.id || m.gcalId))
      );

      // 2. Update projects in UI
      setProjects((prev) =>
        prev.map((p) => {
          const pId = p.id || p.project_id;
          if (pId === tId) {
            const existingIds = new Set((p.meetings || []).map((m) => m.id || m.gcalId));
            const newUnique = updatedMoving.filter(
              (m) => !existingIds.has(m.id || m.gcalId)
            );
            return {
              ...p,
              meetings: [...newUnique, ...(p.meetings || [])],
            };
          }
          return {
            ...p,
            meetings: (p.meetings || []).filter(
              (m) => !meetingIds.includes(m.id || m.gcalId)
            ),
          };
        })
      );

      // 3. Persist to backend
      batchAddProjectMeetings(tId, updatedMoving);
    }
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
            onOpenGoogleCalendarModal={() => setIsGoogleCalendarModalOpen(true)}
            onAssignMeetingsToProject={handleAssignMeetingsToProject}
            gcalSession={gcalSession}
            onToggleDeliverableStatus={handleToggleDeliverableStatus}
            onSelectPrepDoc={handleSelectPrepDoc}
          />
        ) : (
          <ProjectDetailView
            project={activeProject}
            projects={projects}
            backendDocs={backendDocs}
            onBack={() => setActiveProjectId(null)}
            onSelectDoc={setSelectedDoc}
            onAddFileToProject={handleAddFileToProject}
            onRescanProject={handleRescanProject}
            onOpenNewMeetingModal={() => setIsNewMeetingModalOpen(true)}
            onOpenNewDeliverableModal={() => setIsNewDeliverableModalOpen(true)}
            onOpenGoogleCalendarModal={() => setIsGoogleCalendarModalOpen(true)}
            onAssignMeetingsToProject={handleAssignMeetingsToProject}
            gcalSession={gcalSession}
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
        gcalSession={gcalSession}
        setGcalSession={setGcalSession}
      />

      <NewDeliverableModal
        isOpen={isNewDeliverableModalOpen}
        onClose={() => setIsNewDeliverableModalOpen(false)}
        projects={projects}
        activeProject={activeProject}
        onAddDeliverable={handleAddDeliverable}
      />

      <GoogleCalendarModal
        isOpen={isGoogleCalendarModalOpen}
        onClose={() => setIsGoogleCalendarModalOpen(false)}
        projects={projects}
        allMeetings={allMeetings}
        activeProject={activeProject}
        gcalSession={gcalSession}
        setGcalSession={setGcalSession}
        onSyncMeetings={handleSyncGoogleMeetings}
        onAssignMeetingsToProject={handleAssignMeetingsToProject}
        onDisconnectGcal={handleDisconnectGcal}
      />
    </div>
  );
}
