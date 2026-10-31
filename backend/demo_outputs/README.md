# Demo outputs

These four files were **written by hand** (no LLM, no API key). Each has the exact
shape `generate_with_llm` returns: `type, title, content, rationale, depends_on_node_ids`.

| File | Used when r2 (Positioning) is |
|---|---|
| `atlas_cheap_v1`, `nova_cheap_v1` | cheap / budget / deals |
| `atlas_fast_trusted_v2`, `nova_fast_trusted_v2` | anything else (e.g. "fast and trusted") |

`LLM_MODE=mock` serves them through the same validators as real model output.

If the LLM is slow or down while recording: set `LLM_MODE=mock` in `backend/.env`
and restart the server. The cheap -> fast-and-trusted switch then still produces
a visibly different persona and demo page.
