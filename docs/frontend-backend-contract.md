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
