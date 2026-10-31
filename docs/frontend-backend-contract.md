# Frontend / Backend integration contract

Before connecting UI actions, the frontend and backend owners should agree on endpoint paths, request bodies, response shapes, authentication, and WebSocket event names. The frontend API helper is available as `window.BuildifyAPI`.

Suggested initial endpoints (confirm with the backend owner before use):
- `GET /projects/{project_id}`
- `PUT /projects/{project_id}/requirement`
- `GET /agents/status?project_id={project_id}`
- `POST /agents/{agent_name}/start`
- `GET /proposals?project_id={project_id}`
- `POST /proposals/{proposal_id}/approve`
- `POST /proposals/{proposal_id}/reject`
- `POST /proposals/{proposal_id}/redirect`
- `WS /ws/projects/{project_id}`


## Backend status: IMPLEMENTED (see docs/api.md for full request/response shapes)

- Base URL: http://localhost:8000 (CORS is open to all origins)
- Extra endpoints: `POST /agents/{name}/recover`, `POST /agents/{name}/kill`, `POST /reset`
- Agent names: `atlas` (Research & Persona), `nova` (Demo Builder)
- Identity: no login. Send `actor: "niharika"` or `"vaibhav"` in request bodies.
- Errors: `{"detail": {"code": "...", "message": "..."}}`
- Approving a stale proposal returns HTTP 409 with `code: "proposal_stale"` and a `stale_reason`. Show that reason to the user.
- Proposals with `type: "demo_html"` carry a full HTML page in `content`. Render it in an iframe `srcdoc`.
- WebSocket messages all have `{type, project_id, event_id, actor, summary, timestamp, payload}`. `summary` is plain English and can go straight into the timeline.

## LLM configuration (backend/.env, never committed)

- `LLM_API_KEY`: provider key.
- `LLM_PROVIDER`: `gemini` for Google Gemini; leave unset for Anthropic.
- `LLM_MODEL`: optional model override (default `gemini-2.5-flash` for Gemini).
- `LLM_MODE=mock`: serve `backend/demo_outputs/` instead of calling an API.
- If the LLM call fails or times out (25s), the backend falls back to its built-in templates.
