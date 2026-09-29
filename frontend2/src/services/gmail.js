/**
 * Gmail Service for Coordin8.
 *
 * Fetches recent inbox messages using the Gmail REST API v1:
 * - Uses the OAuth access token acquired via Google Identity Services.
 * - Parses message headers (From, Subject, Date) and snippet text.
 * - Auto-matches emails to active projects based on project codes, names, or sender contacts.
 */

import { autoAssignProjectForEvent } from './googleCalendar';

/**
 * Fetch list of recent messages from Gmail.
 * @param {string} accessToken
 * @param {object} options
 * @returns {Promise<Array>}
 */
export async function fetchRecentGmailMessages(accessToken, options = {}) {
  const { maxResults = 25, query = 'newer_than:14d' } = options;

  if (!accessToken) {
    throw new Error('Access token is missing. Please connect your Google account.');
  }

  const listUrl = `https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=${maxResults}&q=${encodeURIComponent(
    query
  )}`;

  const res = await fetch(listUrl, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: 'application/json',
    },
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const message =
      errorData?.error?.message || `Gmail API responded with status ${res.status}`;
    if (res.status === 401) {
      throw new Error(
        'Google session expired or missing Gmail permission. Please disconnect and reconnect Google Workspace.'
      );
    }
    if (res.status === 403) {
      throw new Error(
        'Gmail permission denied. Ensure Gmail API is enabled and scopes are granted in Google Cloud Console.'
      );
    }
    throw new Error(message);
  }

  const data = await res.json();
  const rawList = data.messages || [];

  if (rawList.length === 0) {
    return [];
  }

  // Fetch metadata details for each message (parallel with concurrency limit)
  const detailPromises = rawList.slice(0, maxResults).map(async (msg) => {
    try {
      const detailUrl = `https://gmail.googleapis.com/gmail/v1/users/me/messages/${msg.id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=Date`;
      const detailRes = await fetch(detailUrl, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          Accept: 'application/json',
        },
      });

      if (!detailRes.ok) return null;
      const detailData = await detailRes.json();

      const headers = detailData.payload?.headers || [];
      const getHeader = (name) => {
        const found = headers.find((h) => h.name.toLowerCase() === name.toLowerCase());
        return found ? found.value : '';
      };

      const fromHeader = getHeader('From');
      const subjectHeader = getHeader('Subject') || '(No Subject)';
      const dateHeader = getHeader('Date');

      // Parse sender display name and email address
      let senderName = fromHeader;
      let senderEmail = fromHeader;
      const angleMatch = fromHeader.match(/^(.*?)\s*<([^>]+)>/);
      if (angleMatch) {
        senderName = angleMatch[1].replace(/['"]/g, '').trim() || angleMatch[2];
        senderEmail = angleMatch[2].trim();
      }

      const receivedAt = dateHeader
        ? new Date(dateHeader).toISOString()
        : detailData.internalDate
        ? new Date(parseInt(detailData.internalDate, 10)).toISOString()
        : new Date().toISOString();

      return {
        id: detailData.id,
        threadId: detailData.threadId,
        subject: subjectHeader,
        from: fromHeader,
        senderName,
        senderEmail,
        snippet: detailData.snippet || '',
        receivedAt,
        unread: detailData.labelIds?.includes('UNREAD') || false,
        labels: detailData.labelIds || [],
      };
    } catch (err) {
      console.warn(`Failed fetching detail for message ${msg.id}:`, err);
      return null;
    }
  });

  const resolved = await Promise.all(detailPromises);
  return resolved.filter(Boolean);
}

/**
 * Auto-detect the best project match based on email subject, sender, and snippet.
 * @param {object} email
 * @param {Array} projects
 * @returns {object|null}
 */
export function autoAssignProjectForEmail(email, projects = []) {
  if (!projects || projects.length === 0) return null;
  const text = `${email.subject || ''} ${email.snippet || ''} ${email.senderEmail || ''} ${email.senderName || ''}`.toLowerCase();

  for (const proj of projects) {
    const code = (proj.code || '').toLowerCase();
    const name = (proj.name || '').toLowerCase();

    // Check project code (e.g. "RAG-CORE", "APP-V2")
    if (code && code.length >= 2 && text.includes(code)) {
      return proj;
    }

    // Check significant project keywords
    const keywords = name.split(/\s+/).filter((w) => w.length > 3);
    if (keywords.some((kw) => text.includes(kw))) {
      return proj;
    }
  }

  return null;
}
