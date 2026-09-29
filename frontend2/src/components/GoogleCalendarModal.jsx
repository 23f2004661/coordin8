import React, { useState, useEffect, useMemo } from 'react';
import {
  X,
  Calendar,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Settings,
  ChevronDown,
  ChevronUp,
  LogOut,
  Sparkles,
  Users,
  Video,
  Clock,
  CheckSquare,
  Square,
  Search,
  ArrowRight,
  Filter,
  Layers,
  UserPlus,
} from 'lucide-react';
import {
  getGoogleClientId,
  setCustomGoogleClientId,
  getSavedSession,
  clearSession,
  requestGoogleCalendarAccess,
  fetchCalendarEventsWithToken,
  saveSession,
} from '../services/googleCalendar';
import { fetchGcalAccount } from '../api';

export default function GoogleCalendarModal({
  isOpen,
  onClose,
  projects = [],
  allMeetings = [],
  gcalSession = null,
  setGcalSession,
  onSyncMeetings,
  onAssignMeetingsToProject,
  onDisconnectGcal,
}) {
  const [session, setSession] = useState(gcalSession || getSavedSession());
  const [clientId, setClientId] = useState(getGoogleClientId());
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [showDevSettings, setShowDevSettings] = useState(false);
  const [isSwitchingAccount, setIsSwitchingAccount] = useState(false);

  // Multi-selection state
  const [selectedMeetingIds, setSelectedMeetingIds] = useState([]);
  const [batchTargetProjectId, setBatchTargetProjectId] = useState(
    projects[0]?.id || projects[0]?.project_id || ''
  );

  // Filter & Search
  const [searchQuery, setSearchQuery] = useState('');
  const [projectFilter, setProjectFilter] = useState('all');

  useEffect(() => {
    if (isOpen) {
      const syncActiveSession = async () => {
        try {
          const backendAcc = await fetchGcalAccount();
          if (backendAcc && backendAcc.connected && backendAcc.email) {
            const activeSession = {
              ...(gcalSession || getSavedSession() || {}),
              connected: true,
              mode: backendAcc.mode || 'real',
              user: {
                email: backendAcc.email,
                name: backendAcc.name || backendAcc.email.split('@')[0],
                picture: backendAcc.picture || '',
              },
              lastSync: backendAcc.lastSync || new Date().toISOString(),
              syncedCount: backendAcc.syncedCount || 0,
            };
            setSession(activeSession);
            if (setGcalSession) setGcalSession(activeSession);
            saveSession(activeSession);
            return;
          }
        } catch (err) {
          console.debug('Modal session sync notice:', err);
        }
        const active = gcalSession || getSavedSession();
        setSession(active);
      };

      syncActiveSession();
      setClientId(getGoogleClientId());
      setErrorMsg('');
      setSuccessMsg('');
      setSelectedMeetingIds([]);
      setIsSwitchingAccount(false);
      if (projects.length > 0 && !batchTargetProjectId) {
        setBatchTargetProjectId(projects[0].id || projects[0].project_id);
      }
    }
  }, [isOpen]);

  // Real Google Sign-in popup flow (Initial authorization)
  const handleRealGoogleSignIn = async () => {
    setIsLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const { session: newSession, meetings } = await requestGoogleCalendarAccess(
        null,
        projects
      );
      setSession(newSession);
      if (setGcalSession) setGcalSession(newSession);
      onSyncMeetings(meetings, newSession);
      setSuccessMsg(`Connected as ${newSession.user?.email}! Synced ${meetings.length} events.`);
    } catch (err) {
      console.error('Google Sign-in error:', err);
      setErrorMsg(err.message || 'Failed to authenticate with Google.');
    } finally {
      setIsLoading(false);
    }
  };

  // Sign in with a different Google account (Explicit account selection)
  const handleSwitchAccount = async () => {
    setIsLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const { session: newSession, meetings } = await requestGoogleCalendarAccess(
        null,
        projects,
        { prompt: 'select_account' }
      );
      setSession(newSession);
      if (setGcalSession) setGcalSession(newSession);
      onSyncMeetings(meetings, newSession);
      setIsSwitchingAccount(false);
      setSuccessMsg(`Switched to Google account: ${newSession.user?.email}! Synced ${meetings.length} events.`);
    } catch (err) {
      console.error('Switch account error:', err);
      setErrorMsg(err.message || 'Failed to switch Google account.');
    } finally {
      setIsLoading(false);
    }
  };

  // Re-sync existing connection
  const handleResync = async () => {
    if (!session) return;
    setIsLoading(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      if (session.accessToken) {
        const meetings = await fetchCalendarEventsWithToken(session.accessToken, null, projects);
        const updated = {
          ...session,
          lastSync: new Date().toISOString(),
          syncedCount: meetings.length,
        };
        saveSession(updated);
        setSession(updated);
        if (setGcalSession) setGcalSession(updated);
        onSyncMeetings(meetings, updated);
        setSuccessMsg(`Refreshed ${meetings.length} Google Calendar events for ${session.user?.email}.`);
      } else {
        // Access token missing or expired - prompt re-auth without losing account context
        const { session: newSession, meetings } = await requestGoogleCalendarAccess(
          null,
          projects,
          { prompt: 'consent', hint: session.user?.email }
        );
        setSession(newSession);
        if (setGcalSession) setGcalSession(newSession);
        onSyncMeetings(meetings, newSession);
        setSuccessMsg(`Re-authenticated and refreshed ${meetings.length} events for ${newSession.user?.email}.`);
      }
    } catch (err) {
      console.error('Resync failed:', err);
      setErrorMsg('Google session needs authorization. Click "Switch Account" or re-authenticate.');
    } finally {
      setIsLoading(false);
    }
  };

  // Disconnect
  const handleDisconnect = () => {
    clearSession();
    setSession(null);
    if (setGcalSession) setGcalSession(null);
    setIsSwitchingAccount(false);
    setSuccessMsg('Google Calendar disconnected.');
    if (onDisconnectGcal) onDisconnectGcal();
  };

  // Save custom client ID
  const handleSaveClientId = (e) => {
    e.preventDefault();
    setCustomGoogleClientId(clientId);
    setSuccessMsg('Google Client ID updated successfully.');
  };

  // Filter meetings list
  // Filter meetings list
  const filteredMeetings = useMemo(() => {
    return allMeetings.filter((m) => {
      // Filter by project
      if (projectFilter !== 'all') {
        const mProjId = m.projectId || '';
        if (projectFilter === 'unassigned') {
          if (mProjId) return false;
        } else if (mProjId !== projectFilter) {
          return false;
        }
      }
      // Search query
      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        const titleMatch = (m.title || '').toLowerCase().includes(query);
        const attendeeMatch = (m.attendees || []).some((a) =>
          a.toLowerCase().includes(query)
        );
        const projectMatch = (m.projectName || '').toLowerCase().includes(query);
        return titleMatch || attendeeMatch || projectMatch;
      }
      return true;
    });
  }, [allMeetings, projectFilter, searchQuery]);

  // Checkbox handlers
  const handleToggleMeetingSelect = (id) => {
    setSelectedMeetingIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const handleSelectAllVisible = () => {
    const visibleIds = filteredMeetings.map((m) => m.id || m.gcalId);
    const allSelected = visibleIds.every((id) => selectedMeetingIds.includes(id));
    if (allSelected) {
      setSelectedMeetingIds((prev) => prev.filter((id) => !visibleIds.includes(id)));
    } else {
      setSelectedMeetingIds((prev) => Array.from(new Set([...prev, ...visibleIds])));
    }
  };

  // Batch assign selected meetings to target project or unassigned
  const handleBatchAssign = () => {
    if (selectedMeetingIds.length === 0) return;
    const isUnassigned = !batchTargetProjectId || batchTargetProjectId === 'unassigned';
    const targetProj = projects.find(
      (p) => (p.id || p.project_id) === batchTargetProjectId
    );

    onAssignMeetingsToProject(selectedMeetingIds, isUnassigned ? '' : batchTargetProjectId);
    setSuccessMsg(
      isUnassigned
        ? `Set ${selectedMeetingIds.length} meeting(s) to Unassigned.`
        : `Assigned ${selectedMeetingIds.length} meeting(s) to "${targetProj?.name || 'Project'}".`
    );
    setSelectedMeetingIds([]);
  };

  // Single meeting inline assignment
  const handleSingleAssign = (meetingId, newProjId) => {
    const isUnassigned = !newProjId || newProjId === 'unassigned';
    const targetProj = projects.find((p) => (p.id || p.project_id) === newProjId);
    onAssignMeetingsToProject([meetingId], isUnassigned ? '' : newProjId);
    setSuccessMsg(
      isUnassigned
        ? 'Moved meeting to Unassigned.'
        : `Moved meeting to "${targetProj?.name || 'Project'}".`
    );
  };

  // Format date/time
  const formatTime = (iso) => {
    try {
      const d = new Date(iso);
      return {
        date: d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        time: d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' }),
      };
    } catch {
      return { date: 'Upcoming', time: '' };
    }
  };

  const isAllVisibleSelected =
    filteredMeetings.length > 0 &&
    filteredMeetings.every((m) => selectedMeetingIds.includes(m.id || m.gcalId));

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-container gcal-modal"
        onClick={(e) => e.stopPropagation()}
        style={{ maxWidth: '780px', maxHeight: '90vh' }}
      >
        <div className="modal-header">
          <div className="modal-title-group">
            <div className="gcal-icon-wrapper">
              <Calendar size={22} className="gcal-brand-icon" />
            </div>
            <div>
              <h3 className="modal-title">Google Calendar & Meeting Assignments</h3>
              <span className="modal-subtitle">
                Select and batch-assign calendar meetings across your projects
              </span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        <div className="modal-body gcal-modal-body">
          {/* Status Messages */}
          {errorMsg && (
            <div className="gcal-alert gcal-alert-error">
              <AlertCircle size={18} />
              <div className="alert-content">
                <strong>Authentication Notice</strong>
                <p>{errorMsg}</p>
              </div>
            </div>
          )}

          {successMsg && (
            <div className="gcal-alert gcal-alert-success">
              <CheckCircle2 size={18} />
              <div className="alert-content">
                <p>{successMsg}</p>
              </div>
            </div>
          )}

          {/* Account Status Card */}
          {session?.connected ? (
            <div className="gcal-account-container">
              {/* Connected Google Account Header Strip */}
              <div className="gcal-compact-status-strip">
                <div className="compact-status-left">
                  {session.user?.picture ? (
                    <img
                      src={session.user.picture}
                      alt={session.user.name || session.user.email}
                      className="gcal-avatar-img"
                    />
                  ) : (
                    <div className="gcal-avatar-fallback">
                      {(session.user?.name || session.user?.email || 'G')[0].toUpperCase()}
                    </div>
                  )}
                  <div>
                    <div className="strip-user-row">
                      <strong className="gcal-account-email">{session.user?.email}</strong>
                      <span className="badge badge-success">
                        <span className="live-pulse-dot" /> Connected
                      </span>
                    </div>
                    <span className="strip-subtext">
                      {session.user?.name && `${session.user.name} • `}
                      {allMeetings.length} meetings synced
                      {session.lastSync && (
                        <span> • Last synced {formatTime(session.lastSync).time || 'recently'}</span>
                      )}
                    </span>
                  </div>
                </div>

                <div className="compact-status-right">
                  <button
                    type="button"
                    className="btn btn-secondary btn-sm"
                    onClick={handleResync}
                    disabled={isLoading}
                    title="Pull latest events from this Google Calendar"
                  >
                    <RefreshCw size={13} className={isLoading ? 'spin-anim' : ''} />
                    <span>{isLoading ? 'Syncing...' : 'Sync Calendar'}</span>
                  </button>

                  <button
                    type="button"
                    className={`btn btn-outline btn-sm btn-switch-account ${isSwitchingAccount ? 'active' : ''}`}
                    onClick={() => setIsSwitchingAccount((prev) => !prev)}
                    disabled={isLoading}
                    title="Sign in with a different Google account"
                  >
                    <UserPlus size={13} />
                    <span>{isSwitchingAccount ? 'Close' : 'Switch Account'}</span>
                  </button>

                  <button
                    type="button"
                    className="btn btn-ghost btn-sm text-danger"
                    onClick={handleDisconnect}
                    title="Disconnect Google account"
                  >
                    <LogOut size={13} />
                    <span>Disconnect</span>
                  </button>
                </div>
              </div>

              {/* Reveal "Sign in with a different Google account" section */}
              {isSwitchingAccount && (
                <div className="gcal-switch-account-card">
                  <div className="switch-card-header">
                    <div className="switch-card-title-group">
                      <UserPlus size={15} className="switch-icon" />
                      <div>
                        <h4 className="switch-title">Sign in with a different Google account</h4>
                        <span className="switch-desc">
                          Currently connected as <strong>{session.user?.email}</strong>. Select or log into another Google account below:
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="switch-card-actions">
                    <button
                      type="button"
                      className="btn btn-google-signin switch-google-btn"
                      onClick={handleSwitchAccount}
                      disabled={isLoading}
                    >
                      <svg className="google-svg" viewBox="0 0 24 24" width="18" height="18">
                        <path
                          fill="#4285F4"
                          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                        />
                        <path
                          fill="#34A853"
                          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                        />
                        <path
                          fill="#FBBC05"
                          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                        />
                        <path
                          fill="#EA4335"
                          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                        />
                      </svg>
                      <span>{isLoading ? 'Opening Google Account Chooser...' : 'Sign in with a different Google account'}</span>
                    </button>
                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => setIsSwitchingAccount(false)}
                      disabled={isLoading}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="gcal-status-card disconnected" style={{ padding: '16px' }}>
              <div className="gcal-connect-cta-row">
                <button
                  type="button"
                  className="btn btn-google-signin"
                  onClick={handleRealGoogleSignIn}
                  disabled={isLoading}
                  style={{ width: '100%', justifyContent: 'center' }}
                >
                  <svg className="google-svg" viewBox="0 0 24 24" width="18" height="18">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    />
                  </svg>
                  <span>{isLoading ? 'Opening Google...' : 'Sign in with Google'}</span>
                </button>
              </div>
            </div>
          )}

          {/* ================= MEETING ASSIGNMENT & MULTI-SELECT SECTION ================= */}
          <div className="meetings-assignment-panel">
            <div className="assignment-panel-header">
              <div className="panel-title-group">
                <h4 className="panel-heading">Meeting Project Assignments</h4>
                <span className="panel-count">{allMeetings.length} meetings loaded</span>
              </div>

              {/* Search & Project Filter */}
              <div className="assignment-filters">
                <div className="search-input-wrapper">
                  <Search size={14} />
                  <input
                    type="text"
                    placeholder="Search meetings or attendees..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  {searchQuery && (
                    <button className="clear-search-btn" onClick={() => setSearchQuery('')}>
                      <X size={12} />
                    </button>
                  )}
                </div>

                <div className="filter-select-wrapper">
                  <Filter size={13} />
                  <select
                    value={projectFilter}
                    onChange={(e) => setProjectFilter(e.target.value)}
                  >
                    <option value="all">All Projects & Unassigned</option>
                    <option value="unassigned">Unassigned Only</option>
                    {projects.map((p) => (
                      <option key={p.id || p.project_id} value={p.id || p.project_id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* BATCH ACTION TOOLBAR (Highlighted when meetings are selected) */}
            <div className={`batch-assignment-bar ${selectedMeetingIds.length > 0 ? 'active' : ''}`}>
              <div className="batch-bar-left">
                <button
                  type="button"
                  className="select-all-btn"
                  onClick={handleSelectAllVisible}
                  title={isAllVisibleSelected ? 'Deselect all visible' : 'Select all visible'}
                >
                  {isAllVisibleSelected ? (
                    <CheckSquare size={17} className="check-icon-active" />
                  ) : (
                    <Square size={17} />
                  )}
                  <span>
                    {selectedMeetingIds.length > 0
                      ? `${selectedMeetingIds.length} meeting(s) selected`
                      : 'Select All Visible'}
                  </span>
                </button>
              </div>

              {selectedMeetingIds.length > 0 && (
                <div className="batch-bar-right">
                  <div className="batch-action-controls">
                    <span className="batch-label">Assign selected to:</span>
                    <select
                      value={batchTargetProjectId}
                      onChange={(e) => setBatchTargetProjectId(e.target.value)}
                      className="batch-project-select"
                    >
                      <option value="">Unassigned (No Project)</option>
                      {projects.map((p) => (
                        <option key={p.id || p.project_id} value={p.id || p.project_id}>
                          {p.name} ({p.code || 'PRJ'})
                        </option>
                      ))}
                    </select>

                    <button
                      type="button"
                      className="btn btn-primary btn-sm batch-apply-btn"
                      onClick={handleBatchAssign}
                    >
                      <ArrowRight size={14} />
                      <span>Apply to {selectedMeetingIds.length}</span>
                    </button>

                    <button
                      type="button"
                      className="btn btn-ghost btn-sm"
                      onClick={() => setSelectedMeetingIds([])}
                    >
                      Clear
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* MEETINGS TABLE / LIST */}
            <div className="assigned-meetings-list-container">
              {filteredMeetings.length === 0 ? (
                <div className="empty-meetings-notice">
                  <Calendar size={28} className="empty-icon" />
                  <p>No meetings match your filter.</p>
                  <span>Sync Google Calendar or adjust search terms above.</span>
                </div>
              ) : (
                <div className="assignment-table">
                  {filteredMeetings.map((m) => {
                    const mId = m.id || m.gcalId;
                    const isSelected = selectedMeetingIds.includes(mId);
                    const { date, time } = formatTime(m.startTime);
                    const currentProj = projects.find(
                      (p) => (p.id || p.project_id) === m.projectId
                    );

                    return (
                      <div
                        key={mId}
                        className={`assignment-row ${isSelected ? 'row-selected' : ''}`}
                      >
                        {/* Checkbox */}
                        <div
                          className="row-checkbox-cell"
                          onClick={() => handleToggleMeetingSelect(mId)}
                        >
                          {isSelected ? (
                            <CheckSquare size={18} className="check-icon-active" />
                          ) : (
                            <Square size={18} className="check-icon-idle" />
                          )}
                        </div>

                        {/* Date & Time */}
                        <div className="row-time-cell">
                          <span className="time-date">{date}</span>
                          <span className="time-hour">{time}</span>
                        </div>

                        {/* Meeting Info */}
                        <div className="row-info-cell">
                          <div className="row-title-row">
                            <h5 className="meeting-row-title">{m.title}</h5>
                            {m.isGcal && (
                              <span className="gcal-source-badge" title="Imported from Google Calendar">
                                GCal
                              </span>
                            )}
                            {m.meetUrl && (
                              <a
                                href={m.meetUrl}
                                target="_blank"
                                rel="noreferrer"
                                className="meet-link-badge"
                                title="Open Google Meet in new tab"
                              >
                                <Video size={11} />
                                <span>Meet</span>
                              </a>
                            )}
                          </div>

                          <div className="row-meta-sub">
                            <Users size={12} />
                            <span>{(m.attendees || []).slice(0, 3).join(', ')}</span>
                            {(m.attendees || []).length > 3 && (
                              <span className="attendee-overflow">
                                +{m.attendees.length - 3} more
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Project Assignment Dropdown (Per-meeting inline edit) */}
                        <div className="row-project-cell">
                          <label className="cell-mobile-label">Project:</label>
                          <div
                            className="project-dropdown-container"
                            style={{
                              '--proj-color': m.projectId
                                ? (currentProj?.color || m.projectColor || '#6366f1')
                                : '#94a3b8',
                            }}
                          >
                            <span
                              className="project-color-dot"
                              style={{
                                backgroundColor: m.projectId
                                  ? (currentProj?.color || m.projectColor || '#6366f1')
                                  : '#94a3b8',
                              }}
                            />
                            <select
                              value={m.projectId || ''}
                              onChange={(e) => handleSingleAssign(mId, e.target.value)}
                              className="row-project-select"
                            >
                              <option value="">Unassigned</option>
                              {projects.map((p) => (
                                <option key={p.id || p.project_id} value={p.id || p.project_id}>
                                  {p.name}
                                </option>
                              ))}
                            </select>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          {/* Developer / OAuth Credentials Settings (Expandable) */}
          <div className="gcal-dev-accordion" style={{ marginTop: '8px' }}>
            <button
              type="button"
              className="dev-accordion-toggle"
              onClick={() => setShowDevSettings(!showDevSettings)}
            >
              <div className="accordion-label">
                <Settings size={14} />
                <span>Google Cloud Client ID Settings</span>
              </div>
              {showDevSettings ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {showDevSettings && (
              <div className="dev-accordion-content">
                <form onSubmit={handleSaveClientId} className="client-id-form">
                  <div className="input-group">
                    <input
                      type="text"
                      placeholder="e.g. 123456789-abcdef.apps.googleusercontent.com"
                      value={clientId}
                      onChange={(e) => setClientId(e.target.value)}
                    />
                    <button type="submit" className="btn btn-secondary btn-sm">
                      Save Client ID
                    </button>
                  </div>
                </form>
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <div className="footer-left">
            <span className="footer-hint">
              Selected meetings update automatically across your project timelines & widgets.
            </span>
          </div>
          <button className="btn btn-primary" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
