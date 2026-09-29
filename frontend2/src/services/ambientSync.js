/**
 * Ambient Ingestion Engine for Coordin8.
 *
 * Implements Pillar 1 (Ambient Ingestion over Manual Entry):
 * - Periodically and silently checks connected communication channels (Gmail) in the background.
 * - Extracts context without requiring user clicks or showing an inbox view.
 * - Bridges raw inbound communications with backend deliverable intelligence.
 */

import { useEffect, useRef, useState } from 'react';
import { fetchRecentGmailMessages, autoAssignProjectForEmail } from './gmail';
import { syncEmailsWithBackend, fetchSyncedEmails } from '../api';

const AMBIENT_POLL_INTERVAL_MS = 10 * 60 * 1000; // 10 minutes

/**
 * Perform a single silent ambient sync pass across Gmail.
 * @param {string} accessToken
 * @param {Array} projects
 * @returns {Promise<{ success: boolean, count: number, error?: string }>}
 */
export async function performSilentAmbientSync(accessToken, projects = []) {
  if (!accessToken) {
    return { success: false, count: 0, error: 'No active session' };
  }

  try {
    const rawMsgs = await fetchRecentGmailMessages(accessToken, {
      maxResults: 20,
      query: 'is:inbox -category:promotions -category:social newer_than:7d',
    });

    if (!rawMsgs || rawMsgs.length === 0) {
      return { success: true, count: 0 };
    }

    const mapped = rawMsgs.map((m) => {
      const matchedProj = autoAssignProjectForEmail(m, projects);
      return {
        ...m,
        projectId: matchedProj ? (matchedProj.id || matchedProj.project_id) : null,
        projectName: matchedProj ? matchedProj.name : null,
        projectColor: matchedProj ? (matchedProj.color || '#6366f1') : '#94a3b8',
      };
    });

    await syncEmailsWithBackend(mapped);
    return { success: true, count: mapped.length };
  } catch (err) {
    console.debug('[AmbientSync] Silent sync notice:', err.message);
    return { success: false, count: 0, error: err.message };
  }
}

/**
 * React hook to manage silent ambient background ingestion.
 */
export function useAmbientSync({ session, projects = [], onSyncComplete }) {
  const [ambientState, setAmbientState] = useState({
    isActive: Boolean(session?.connected && session?.accessToken),
    isSyncing: false,
    lastSyncedAt: null,
    analyzedCount: 0,
  });

  const isSyncingRef = useRef(false);

  useEffect(() => {
    if (!session?.connected || !session?.accessToken) {
      setAmbientState((prev) => ({ ...prev, isActive: false }));
      return;
    }

    setAmbientState((prev) => ({ ...prev, isActive: true }));

    const triggerSync = async () => {
      if (isSyncingRef.current) return;
      isSyncingRef.current = true;
      setAmbientState((prev) => ({ ...prev, isSyncing: true }));

      const res = await performSilentAmbientSync(session.accessToken, projects);

      isSyncingRef.current = false;
      setAmbientState((prev) => ({
        ...prev,
        isSyncing: false,
        lastSyncedAt: res.success ? new Date().toISOString() : prev.lastSyncedAt,
        analyzedCount: res.count > 0 ? res.count : prev.analyzedCount,
      }));

      if (res.success && onSyncComplete) {
        onSyncComplete(res);
      }
    };

    // Initial silent sync on mount / session activation (delayed by 3s so initial page load is instant)
    const initialTimer = setTimeout(triggerSync, 3000);

    // Periodic silent background timer
    const intervalTimer = setInterval(triggerSync, AMBIENT_POLL_INTERVAL_MS);

    return () => {
      clearTimeout(initialTimer);
      clearInterval(intervalTimer);
    };
  }, [session?.connected, session?.accessToken, projects.length]);

  return ambientState;
}
