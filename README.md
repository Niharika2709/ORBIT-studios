# Buildify Studio

This repository starts with the existing Buildify Studio frontend, separated into HTML, CSS, and JavaScript files. The existing UI and scroll interactions are preserved.

## Folder structure

```text
Buildify-Studio/
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   ├── js/api.js
│   ├── js/app.js
│   └── assets/
├── backend/
├── docs/
├── tests/
├── .gitignore
└── README.md
```

## Run the frontend in VS Code

1. Open this folder in VS Code.
2. Install the **Live Server** extension if it is not already installed.
3. Right-click `frontend/index.html`.
4. Select **Open with Live Server**.

The frontend currently preserves the existing prototype behavior. `frontend/js/api.js` provides a shared API helper for the backend integration phase.

## Backend URL

The default API URL is `http://127.0.0.1:8000`. To change it, define `window.BUILDIFY_API_URL` before loading `js/api.js` in `frontend/index.html`.

## Team workflow

- `main`: reviewed, integrated code.
- `feature/frontend`: frontend work.
- `feature/backend`: backend work.
- `feature/ai-agents`: Atlas and Nova.
- `feature/context-integration`: context, versioning, integration, and tests.

Create a feature branch, commit your changes, push the branch, and open a Pull Request. Do not commit API keys or `.env` files.
