# Coordin8 LM Studio Diagnosis

Date: 2026-10-02. Model: `meta-llama-3.1-8b-instruct`.

## Verified Root Cause

The LM Studio chat-template path inserts function-calling instructions into a
request that contains no tools. This was observed using the supported command:

```powershell
& "$env:USERPROFILE\.lmstudio\bin\lms.exe" log stream --source model --filter input --json
```

For a minimal request asking for two sentences about project managers, the
formatted model input contained:

```text
Environment: ipython
...
Given the following functions, please respond with a JSON for a function call with its proper arguments that best answers the given prompt.

Respond in the format {"name": function name, "parameters": dictionary of argument name and its value}.Do not use variables.

Explain what a project manager does in two sentences.
```

There were no function definitions between the instructions and the question.
The cached model template gates these instructions on `tools is not none` and
`tools_in_user_message and not tools is none`, rather than on a nonempty tool
list. The no-tools path therefore enters the function-calling branch. This is a
template/tool-mode interaction, not an invalid Coordin8 role or message format.

The API returns literal function-call-shaped JSON in `message.content` and an
empty `message.tool_calls` array. Coordin8 was reading the correct response
field. MoM parsing correctly rejects this output because its required fields
are not at the top level. Ordinary MoM JSON instructions are not tool definitions.

The reported manual template normalization/reload was retested. The active API
model still produced the exact same injected instructions. Recovery is not
verified, and the model was not replaced.

## Request Trace

Project Chat:

1. `initProjectChat` in `frontend/js/app.js` calls `Coordin8Api.chat`.
2. `frontend/js/api.js` posts `{"message": "..."}` to the selected project's
   `/api/projects/{project_id}/chat` endpoint with the user's bearer token.
3. `backend/app/api/projects.py` checks project access before retrieval.
4. `KnowledgeBase.query_context` in `backend/app/knowledge_base.py` runs document,
   section, and chunk retrieval, rank fusion, reranking, and context assembly.
5. `backend/app/retrieval/context.py` formats sanitized evidence with citations.
6. `build_rag_prompt` in `backend/app/llm/prompts.py` combines evidence and question.
7. `LLMClient.generate_answer` calls `generate_completion`, which posts the body
   below to LM Studio. LM Studio applies the model template after receiving it.

MoM:

1. The Meetings view calls `Coordin8Api.generateMom`.
2. The frontend posts to `/api/meetings/{meeting_id}/generate-mom`.
3. `backend/app/api/meetings.py` authorizes access and constructs system/user
   prompts from the stored transcript; it does not run RAG for this operation.
4. `LLMClient.generate_completion` uses the same chat-completions transport.
5. The existing meeting route parses the expected JSON and persists extracted
   minutes/action items only after valid generation. This route was not changed.

## Exact Captured Project Chat Body

Destination: `http://127.0.0.1:1234/v1/chat/completions`.

```json
{
  "model": "meta-llama-3.1-8b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "You are Coordin8, a high-precision multimodal RAG assistant.\nYour answers MUST be strictly grounded in the provided EVIDENCE ITEMS.\n\nRULES:\n1. Only answer using facts explicitly stated in the EVIDENCE ITEMS.\n2. If the evidence does not contain sufficient information to answer the question, state clearly: \"I cannot answer this question based on the provided documents.\" Do NOT invent or extrapolate facts.\n3. Every substantive claim must include its source citation in brackets, e.g. [Doc doc_123 (Page 14)] or [Doc doc_456 (Slide 3)].\n4. Never invent or hallucinate citations. If a citation is not in the evidence, do not cite it.\n5. Format your response cleanly in Markdown.\n"
    },
    {
      "role": "user",
      "content": "CONTEXT EVIDENCE:\n--- EVIDENCE ITEM [1] ---\nSource: Doc doc_5ceea85f298b (Section sec_doc_5ceea85f298b_main)\nContent:\nQ3 Onboarding verification code is COORDIN8_Q3_20261002. The approved project delivery date is 2026-10-16. Anjali Gupta owns the project. This document belongs only to Q3 Onboarding.\n\n--- EVIDENCE ITEM [2] ---\nSource: Doc doc_98eb257f1b2a (Section sec_doc_98eb257f1b2a_main)\nContent:\nCoordin8 verification meeting on 2026-10-02. Anjali Gupta: We decided to use the shared tracker as the source of truth. Tarang Jhaveri: I will validate the onboarding checklist by 2026-10-09. Anjali Gupta: I will approve the client access list by 2026-10-12.\n\n\nUSER QUESTION:\nWhat is the Q3 Onboarding approved project delivery date? Answer briefly with a citation.\n\nPlease provide a grounded, truthful answer with citations to the evidence above."
    }
  ],
  "temperature": 0.1
}
```

## Exact Captured MoM Body

Same destination and transport options as Project Chat.

```json
{
  "model": "meta-llama-3.1-8b-instruct",
  "messages": [
    {
      "role": "system",
      "content": "Extract minutes from the supplied meeting transcript. Return only valid JSON. Do not invent names, dates, decisions, or tasks. Use null for unknown owners or dates."
    },
    {
      "role": "user",
      "content": "Return keys \"summary\" (string), \"decisions\" (array of strings), and \"action_items\" (array of objects with \"text\", \"owner\", and \"due_date\" as YYYY-MM-DD or null).\n\nMeeting transcript:\nCoordin8 verification meeting on 2026-10-02. Anjali Gupta: We decided to use the shared tracker as the source of truth. Tarang Jhaveri: I will validate the onboarding checklist by 2026-10-09. Anjali Gupta: I will approve the client access list by 2026-10-12."
    }
  ],
  "temperature": 0.1
}
```

For both workflows:

| Option | Actual value |
|---|---|
| `tools` | Omitted |
| `tool_choice` | Omitted |
| `functions` / `function_call` | Omitted |
| `response_format` | Omitted |
| `max_tokens` | Omitted; server/model default applies |
| `stream` | Omitted |
| `temperature` | `0.1` |
| Explicit headers | `Authorization: Bearer <redacted>`, `Content-Type: application/json` |
| HTTP client timeout | `60.0` seconds |

API key values are deliberately redacted. No custom template or function header
is sent. These payloads remain unchanged after the client safeguard.

## Direct Comparison Results

All requests used `/v1/chat/completions` and the same loaded model.

| Request | HTTP | Observed `message.content` |
|---|---|---|
| Minimal user-only request, no tools/options | 200 | `{"name":"explain_job","parameters":{"topic":"project manager","length":2}}` |
| System/user messages with Coordin8's temperature | 200 | `{"name":"explain","parameters":{"topic":"project manager","num_sentences":2}}` |
| Exact captured Project Chat body | 200 | `{"name":"function","parameters":{"project_delivery_date":"2026-10-16"}}` |
| Exact captured MoM body | 200 | `extract_minutes` function wrapper; required MoM fields absent at top level |
| Minimal request after reported template fix/reload | 200 | Function wrapper again; injected model input unchanged |

The minimal and Coordin8 requests both fail to produce the intended content.
The temperature, RAG prompt, and MoM parser are not the source of the injected
function-calling instruction.

## Minimal Code Safeguard

Only `backend/app/llm/client.py` and its existing unit test file were edited.
The client now rejects explicit tool/function calls, empty text, and JSON
`name`/`parameters` wrappers. Normal text and normal MoM JSON pass through
unchanged. `generate_answer` preserves the specific error. There are no fake
answers, retries with fabricated content, prompt rewrites, or transport changes.

This is an honest-error safeguard, not a claim that generation has been repaired.
The existing Project Chat route now returns HTTP 502 with:

```json
{"detail":"AI service returned a function call. Check LM Studio's prompt template."}
```

The unchanged MoM route returns its existing generic AI-service HTTP 502 error
when the client rejects the function-call response. No generated action items
were fabricated or persisted.

## Verification

- Focused LLM tests: 6 passed.
- Complete backend suite: 55 passed, 28 warnings; isolated temporary SQLite and
  disconnected Qdrant URL, never the live PostgreSQL database/collections.
- Live login and project evidence retrieval: passed.
- Live project isolation: unauthorized documents, search, and chat each returned
  403. Retrieved Q3 evidence did not contain the ACME-only verification marker.
- Live Project Chat: executed, HTTP 502 with the template-specific error.
- Live MoM: executed, HTTP 502; structured minutes/action items remain blocked.
- Browser login, project switching, and Project Chat error display: executed.
- Browser Meetings and MoM generation: executed with a clean manager session;
  HTTP 502 and the existing AI-service alert, with no JavaScript errors during
  that check. No generated minutes or action items were produced.
- A rapid browser role/project switch surfaced an existing `renderJiraMetrics`
  null-data exception. Frontend code was not changed under the task restrictions.

Authentication, PostgreSQL/Qdrant settings, Docker containers, frontend, project
authorization, task/meeting logic, and embeddings were not modified in this task.

## Remaining External Fix

In LM Studio's prompt-template override for the API model, immediately after its
existing `custom_tools` block, normalize an omitted/empty tool list:

```jinja
{%- if tools is not defined or not tools %}
    {%- set tools = none %}
{%- endif %}
```

Save/apply it to the same API model and reload that model if necessary. The fix
is active only when `lms log stream` no longer shows the inserted function-call
instructions for a no-tools request. Retest the direct minimal request, cited
Project Chat, and real MoM extraction before declaring either AI workflow ready.