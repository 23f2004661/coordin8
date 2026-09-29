/**
 * Google Calendar Integration Service for Coordin8.
 *
 * Utilizes Google Identity Services (GIS) OAuth 2.0 Token Client:
 * - End-users authenticate via standard Google popup.
 * - Queries primary Google Calendar events via the Google Calendar REST API v3.
 * - Smartly maps calendar events to projects or allows granular multi-selection.
 */

import { saveGcalAccount, deleteGcalAccount } from '../api';

const STORAGE_SESSION_KEY = 'coordin8_gcal_session';
const STORAGE_CLIENT_ID_KEY = 'coordin8_gcal_client_id';

export function getGoogleClientId() {
  const custom = localStorage.getItem(STORAGE_CLIENT_ID_KEY);
  if (custom && custom.trim()) return custom.trim();
  return (import.meta.env.VITE_GOOGLE_CLIENT_ID || '').trim();
}

export function setCustomGoogleClientId(id) {
  if (id && id.trim()) {
    localStorage.setItem(STORAGE_CLIENT_ID_KEY, id.trim());
  } else {
    localStorage.removeItem(STORAGE_CLIENT_ID_KEY);
  }
}

export function getSavedSession() {
  try {
    const raw = localStorage.getItem(STORAGE_SESSION_KEY);
    if (!raw) return null;
    const session = JSON.parse(raw);
    if (session?.mode === 'demo') {
      localStorage.removeItem(STORAGE_SESSION_KEY);
      return null;
    }
    return session;
  } catch (err) {
    return null;
  }
}

export function saveSession(session) {
  try {
    localStorage.setItem(STORAGE_SESSION_KEY, JSON.stringify(session));
    if (session && session.connected) {
      saveGcalAccount({
        connected: true,
        email: session.user?.email || '',
        name: session.user?.name || '',
        picture: session.user?.picture || '',
        mode: session.mode || 'real',
        lastSync: session.lastSync || new Date().toISOString(),
        syncedCount: session.syncedCount || 0,
      });
    }
  } catch (err) {
    console.warn('Could not save GCal session:', err);
  }
}

export function clearSession() {
  localStorage.removeItem(STORAGE_SESSION_KEY);
  deleteGcalAccount();
}

/**
 * Auto-detects the best project match based on meeting title and description.
 */
export function autoAssignProjectForEvent(item, projects = []) {
  if (!projects || projects.length === 0) return null;
  const text = `${item.summary || ''} ${item.description || ''}`.toLowerCase();

  for (const proj of projects) {
    const code = (proj.code || '').toLowerCase();
    const name = (proj.name || '').toLowerCase();
    if (code && code.length >= 2 && text.includes(code)) return proj;

    const keywords = name.split(/\s+/).filter((w) => w.length > 3);
    if (keywords.some((kw) => text.includes(kw))) {
      return proj;
    }
  }

  return projects[0];
}

/**
 * Strips legacy prefixes like 'Agenda:' and suffixes like 'Scheduled via Coordin8 Workspace'.
 */
export function cleanAgendaText(text) {
  if (!text) return '';
  return String(text)
    .replace(/^Agenda:\s*/im, '')
    .replace(/\s*Scheduled via Coordin8 Workspace\s*/gim, '')
    .trim();
}

/**
 * Normalizes a Google Calendar API event item into Coordin8 Meeting structure.
 */
export function normalizeGoogleEvent(item, targetProject = null, allProjects = []) {
  const assignedProj = targetProject || null;

  const startRaw = item.start?.dateTime || item.start?.date || new Date().toISOString();
  const endRaw = item.end?.dateTime || item.end?.date || startRaw;

  // Extract Meet URL if available
  let meetUrl = item.hangoutLink || '';
  if (!meetUrl && item.conferenceData?.entryPoints) {
    const videoEntry = item.conferenceData.entryPoints.find(
      (ep) => ep.entryPointType === 'video'
    );
    if (videoEntry?.uri) meetUrl = videoEntry.uri;
  }

  // Extract attendees
  const attendees = (item.attendees || []).map(
    (att) => att.displayName || att.email || 'Guest'
  );

  return {
    id: `gcal_${item.id}`,
    gcalId: item.id,
    title: item.summary || 'Untitled Calendar Event',
    projectId: assignedProj ? (assignedProj.id || assignedProj.project_id) : null,
    projectName: assignedProj ? assignedProj.name : 'Unassigned',
    projectColor: assignedProj ? assignedProj.color : '#94a3b8',
    startTime: startRaw,
    endTime: endRaw,
    platform: meetUrl ? 'Google Meet' : 'Google Calendar',
    meetUrl: meetUrl || null,
    attendees: attendees.length > 0 ? attendees : ['You (Organizer)'],
    agenda: cleanAgendaText(item.description),
    prepDoc: '',
    status: item.status === 'cancelled' ? 'cancelled' : 'confirmed',
    isGcal: true,
    htmlLink: item.htmlLink || null,
  };
}

/**
 * Fetch calendar events using a valid Google OAuth access token.
 */
export async function fetchCalendarEventsWithToken(accessToken, targetProject = null, allProjects = []) {
  const timeMin = new Date().toISOString();
  const endpoint = `https://www.googleapis.com/calendar/v3/calendars/primary/events?timeMin=${encodeURIComponent(
    timeMin
  )}&singleEvents=true&orderBy=startTime&maxResults=30`;

  const res = await fetch(endpoint, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: 'application/json',
    },
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(
      errData.error?.message || `Google Calendar API error: HTTP ${res.status}`
    );
  }

  const data = await res.json();
  const items = data.items || [];
  return items.map((item) => normalizeGoogleEvent(item, targetProject, allProjects));
}

/**
 * Fetch Google user profile info (name, email, avatar).
 */
export async function fetchGoogleUserProfile(accessToken) {
  try {
    const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (res.ok) {
      return await res.json();
    }
  } catch (err) {
    console.warn('Could not fetch user profile:', err);
  }
  return { email: 'user@gmail.com', name: 'Google Workspace User' };
}

/**
 * Triggers the official Google Identity Services OAuth 2.0 popup.
 * Supports options: { prompt: 'consent' | 'select_account' | '', hint: 'user@email.com' }
 */
export const GCAL_SCOPES =
  'https://www.googleapis.com/auth/calendar.events https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile';

/**
 * Parses user duration text (e.g. "45 min", "1 hr", "90 minutes", "30") into integer minutes.
 */
export function parseDurationMinutes(durationStr) {
  if (!durationStr) return 30;
  const str = String(durationStr).toLowerCase().trim();
  const hrMatch = str.match(/(\d+(\.\d+)?)\s*(?:h|hr|hour|hours)/);
  const minMatch = str.match(/(\d+)\s*(?:m|min|minute|minutes)/);
  if (hrMatch) {
    const hours = parseFloat(hrMatch[1]);
    const mins = minMatch ? parseInt(minMatch[1], 10) : 0;
    return Math.round(hours * 60) + mins;
  }
  if (minMatch) {
    return parseInt(minMatch[1], 10);
  }
  const justNum = parseInt(str, 10);
  if (!isNaN(justNum) && justNum > 0) return justNum;
  return 30;
}

/**
 * Extracts list of attendee emails from comma/semicolon/newline separated string.
 */
export function parseAttendeeEmails(input) {
  if (!input) return [];
  const parts = String(input).split(/[,;\n]+/).map((s) => s.trim()).filter(Boolean);
  const emails = [];
  for (const part of parts) {
    const angleMatch = part.match(/<([^>]+)>/);
    if (angleMatch && angleMatch[1].includes('@')) {
      emails.push(angleMatch[1].trim());
    } else if (part.includes('@')) {
      emails.push(part.replace(/['"<>\s]/g, '').trim());
    } else {
      emails.push(part.trim());
    }
  }
  return emails;
}

/**
 * Requests an OAuth 2.0 access token via Google Identity Services Token Client.
 */
export function requestGoogleAccessToken(options = {}) {
  return new Promise((resolve, reject) => {
    const clientId = getGoogleClientId();
    if (!clientId) {
      reject(
        new Error(
          'Google Client ID is not configured. Please enter your Client ID in Settings or .env file.'
        )
      );
      return;
    }

    if (!window.google?.accounts?.oauth2) {
      reject(
        new Error(
          'Google Identity Services SDK is still loading. Please check your internet connection and try again.'
        )
      );
      return;
    }

    try {
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: GCAL_SCOPES,
        callback: async (tokenResponse) => {
          if (tokenResponse.error) {
            reject(new Error(tokenResponse.error_description || tokenResponse.error));
            return;
          }

          try {
            const accessToken = tokenResponse.access_token;
            const user = await fetchGoogleUserProfile(accessToken);
            const current = getSavedSession() || {};
            const session = {
              ...current,
              connected: true,
              mode: 'real',
              accessToken,
              user: user || current.user,
              lastSync: new Date().toISOString(),
            };
            saveSession(session);
            resolve({ accessToken, session, user });
          } catch (syncErr) {
            reject(syncErr);
          }
        },
        error_callback: (err) => {
          reject(new Error(err?.message || 'Google authorization window was closed.'));
        },
      });

      const tokenRequestOptions = {};
      if (options.prompt !== undefined) {
        tokenRequestOptions.prompt = options.prompt;
      } else {
        tokenRequestOptions.prompt = 'consent';
      }
      if (options.hint) {
        tokenRequestOptions.hint = options.hint;
      } else {
        const saved = getSavedSession();
        if (saved?.user?.email) {
          tokenRequestOptions.hint = saved.user.email;
        }
      }

      client.requestAccessToken(tokenRequestOptions);
    } catch (err) {
      reject(err);
    }
  });
}

/**
 * Triggers the official Google Identity Services OAuth 2.0 popup and syncs events.
 * Supports options: { prompt: 'consent' | 'select_account' | '', hint: 'user@email.com' }
 */
export function requestGoogleCalendarAccess(targetProject = null, allProjects = [], options = {}) {
  return new Promise((resolve, reject) => {
    const clientId = getGoogleClientId();

    if (!clientId) {
      reject(
        new Error(
          'Google Client ID is not configured. Please enter your Client ID in Settings or try Demo Mode.'
        )
      );
      return;
    }

    if (!window.google?.accounts?.oauth2) {
      reject(
        new Error(
          'Google Identity Services SDK is still loading. Please check your internet connection and try again.'
        )
      );
      return;
    }

    try {
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: GCAL_SCOPES,
        callback: async (tokenResponse) => {
          if (tokenResponse.error) {
            reject(new Error(tokenResponse.error_description || tokenResponse.error));
            return;
          }

          try {
            const accessToken = tokenResponse.access_token;
            const user = await fetchGoogleUserProfile(accessToken);
            const meetings = await fetchCalendarEventsWithToken(accessToken, targetProject, allProjects);

            const session = {
              connected: true,
              mode: 'real',
              accessToken,
              user,
              lastSync: new Date().toISOString(),
              syncedCount: meetings.length,
            };
            saveSession(session);

            resolve({ session, meetings });
          } catch (syncErr) {
            reject(syncErr);
          }
        },
        error_callback: (err) => {
          reject(new Error(err?.message || 'Google authorization window was closed.'));
        },
      });

      const tokenRequestOptions = {};
      if (options.prompt !== undefined) {
        tokenRequestOptions.prompt = options.prompt;
      } else {
        tokenRequestOptions.prompt = 'consent';
      }
      if (options.hint) {
        tokenRequestOptions.hint = options.hint;
      }

      client.requestAccessToken(tokenRequestOptions);
    } catch (err) {
      reject(err);
    }
  });
}

/**
 * Creates a new event in Google Calendar with an automatic Google Meet video conference,
 * invites the specified attendees, and returns the normalized Coordin8 meeting object.
 */
export async function createGoogleCalendarEvent({
  title,
  date,
  time,
  duration = '30 min',
  attendees = '',
  agenda = '',
  prepDoc = '',
  targetProject = null,
  allProjects = [],
}) {
  if (!title || !title.trim()) {
    throw new Error('Meeting title is required.');
  }

  // Parse start date/time
  const startObj = new Date(`${date}T${time}:00`);
  if (isNaN(startObj.getTime())) {
    throw new Error('Please specify a valid meeting date and time.');
  }

  const durationMins = parseDurationMinutes(duration);
  const endObj = new Date(startObj.getTime() + durationMins * 60 * 1000);
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC';

  // Parse attendees list
  const attendeeEmails = Array.isArray(attendees)
    ? attendees
    : parseAttendeeEmails(attendees);

  const apiAttendees = attendeeEmails
    .filter((e) => typeof e === 'string' && e.includes('@'))
    .map((email) => ({ email: email.trim() }));

  const cleanAgenda = cleanAgendaText(agenda);

  const eventPayload = {
    summary: title.trim(),
    description: cleanAgenda,
    start: {
      dateTime: startObj.toISOString(),
      timeZone,
    },
    end: {
      dateTime: endObj.toISOString(),
      timeZone,
    },
    conferenceData: {
      createRequest: {
        requestId: `c8_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
        conferenceSolutionKey: {
          type: 'hangoutsMeet',
        },
      },
    },
  };

  if (apiAttendees.length > 0) {
    eventPayload.attendees = apiAttendees;
  }

  const postEvent = async (token) => {
    const endpoint =
      'https://www.googleapis.com/calendar/v3/calendars/primary/events?conferenceDataVersion=1&sendUpdates=all';
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(eventPayload),
    });
    return res;
  };

  let session = getSavedSession();
  let accessToken = session?.accessToken;
  let res = null;

  if (accessToken) {
    try {
      res = await postEvent(accessToken);
    } catch (netErr) {
      console.warn('Network issue or token error with cached access token:', netErr);
      res = null;
    }
  }

  // If no token or token was rejected (expired / 401 or insufficient scope / 403)
  if (!res || res.status === 401 || res.status === 403) {
    const authResult = await requestGoogleAccessToken({
      prompt: 'consent',
      hint: session?.user?.email,
    });
    accessToken = authResult.accessToken;
    session = authResult.session;
    res = await postEvent(accessToken);
  }

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    const message =
      errData.error?.message || `Google Calendar API error: HTTP ${res.status}`;
    throw new Error(message);
  }

  const data = await res.json();

  // Extract generated Meet URL
  let meetUrl = data.hangoutLink || '';
  if (!meetUrl && data.conferenceData?.entryPoints) {
    const videoEntry = data.conferenceData.entryPoints.find(
      (ep) => ep.entryPointType === 'video'
    );
    if (videoEntry?.uri) meetUrl = videoEntry.uri;
  }

  const assignedProj = targetProject || null;
  const finalAttendees =
    attendeeEmails.length > 0
      ? attendeeEmails
      : [data.organizer?.email || session?.user?.email || 'You (Organizer)'];

  const coordin8Meeting = {
    id: `gcal_${data.id}`,
    gcalId: data.id,
    title: data.summary || title.trim(),
    projectId: assignedProj ? (assignedProj.id || assignedProj.project_id) : null,
    projectName: assignedProj ? assignedProj.name : 'Unassigned',
    projectColor: assignedProj ? assignedProj.color : '#94a3b8',
    startTime: data.start?.dateTime || startObj.toISOString(),
    endTime: data.end?.dateTime || endObj.toISOString(),
    duration: duration || `${durationMins} min`,
    platform: meetUrl ? 'Google Meet' : 'Google Calendar',
    meetUrl: meetUrl || null,
    attendees: finalAttendees,
    agenda: agenda?.trim() || '',
    prepDoc: prepDoc?.trim() || '',
    status: 'confirmed',
    isGcal: true,
    htmlLink: data.htmlLink || null,
  };

  // Update session syncedCount
  if (session && session.connected) {
    const updatedSession = {
      ...session,
      syncedCount: (session.syncedCount || 0) + 1,
      lastSync: new Date().toISOString(),
    };
    saveSession(updatedSession);
  }

  return { meeting: coordin8Meeting, rawEvent: data, session: getSavedSession() };
}


