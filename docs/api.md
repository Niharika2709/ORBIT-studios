# ORBIT API Reference

Base URL: http://localhost:8000
Interactive docs: http://localhost:8000/docs
Errors: {"detail": {"code": "...", "message": "..."}}
Valid actors: niharika, vaibhav
Agent ids: atlas (Research & Persona), nova (Demo Builder)

## REST endpoints

| Endpoint | Request body | Response |
|---|---|---|
| GET /projects/1 | none | {id, name, goal, requirement, users[], nodes[], artifact, decisions[], events[last 30]} |
| PUT /projects/1/requirement | {text, actor, node_id?} | {requirement, affected_node_ids[], stale_proposal_ids[], notified_agents[]} |
| GET /agents/status?project_id=1 | none | {project_id, requirement_version, agents[]} |
| POST /agents/atlas/start, /agents/nova/start | optional {project_id, task?, actor} | {agent} |
| POST /agents/{id}/kill | optional | {agent} |
| POST /agents/{id}/recover | optional {project_id, actor} | {agent, context_packet} |
| GET /proposals?project_id=1&status=? | none | {project_id, proposals[]} (newest first) |
| POST /proposals/{id}/approve | {actor, note?} | {proposal, artifact} or 409 proposal_stale / already_decided |
| POST /proposals/{id}/reject | {actor, note?} | {proposal} |
| POST /proposals/{id}/redirect | {actor, instruction} | {proposal, agent} |
| POST /reset | none | {ok: true} |

## WebSocket: ws://localhost:8000/ws/projects/1

Every message: {type, project_id, event_id, actor, summary, timestamp, payload}

| type | payload |
|---|---|
| connected | {requirement_version} |
| requirement_updated | {requirement, changed_node_id, affected_node_ids[]} |
| agents_notified | {agent_ids[], requirement_version, agents[]} |
| agent_status_changed | {agent} |
| agent_recovered | {agent_id, context_packet} |
| proposal_created | {proposal} |
| proposal_stale | {proposal_id, stale_reason, based_on_version, current_version} |
| proposal_approved | {proposal_id, note} |
| proposal_rejected | {proposal_id, note} |
| proposal_redirected | {proposal_id, instruction} |
| artifact_updated | {artifact} |
| state_reset | {} |