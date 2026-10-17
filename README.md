# abrar-cloud

AbrarCloud is a modular personal-cloud backend by Syed Abrar Ali: one FastAPI application that auto-discovers and mounts seventeen feature modules (account sign-up, login, e-mail verification, password reset, a file workspace, document/image/audio parsers, image and speech generators, a database editor, an agent-driven document editor and placeholder editors for PDF, slides, spreadsheets and images) under one API, and serves the matching HTML pages from a `templates/` folder. It is the server side of a self-hosted "cloud" workspace: users register, log in with a JWT, keep files in a workspace directory, and call tools that parse or create files there. Every capability that could need a paid external model has a local fallback, so the whole server runs on a small machine with no API keys at all.

## Where it is used

It runs on the owner's machine as the back end for a set of browser pages (login, sign-up, file tools) during development of a personal cloud. The `Plan/` folder holds one blueprint per module and `progress.md` is the running log of what has been built, so the repository doubles as the design record for the project.

## How it works

### Core (`backend/`)

| File | Role |
| --- | --- |
| `main.py` | Creates the FastAPI app with permissive CORS, then for each name in `MODULES` imports `backend.<name>.router`, falling back to `backend.<name>.main`, and mounts its `router` at `/<name>`. Failures are logged and skipped, so one broken module never stops the server. Mounts the integration router at `/backend/router` and exposes `GET /` with status and the module list. `python -m backend.main` starts uvicorn with reload. |
| `router.py` | Integration bridge: `GET /backend/router` renders an index of every folder in `templates/`; `GET /backend/router/templates/{name}` returns that folder's `index.html`, or a styled "coming soon" page when missing; `/health`. |
| `config.py` | `pydantic-settings` `Settings`: base, `userfiles/` and `tasks/` directories (created on import), JWT secret/algorithm/expiry (24 h), optional provider API keys, `HOST`/`PORT` (default `0.0.0.0:8000`). Reads `.env`. |
| `database.py` | SQLite at `backend/abrar_cloud.db`, created on import with `users` (real_name, unique username and e-mail, password hash, verified flag) and `verification_codes` (e-mail, code, expiry). |
| `utils/auth.py` | bcrypt hashing through passlib (SHA-256 fallback when passlib is missing), `create_access_token` / `decode_access_token` with python-jose HS256. |
| `utils/agent.py` | Workspace tools (`read_user_file`, `write_user_file`, `list_user_files`) and `OpenManusAgent`: when LangChain and a provider key are available it builds a tool-calling agent over those three tools; otherwise `_execute_fallback` is a rule-based mock that lists, reads or writes files based on keywords in the instruction. |
| `test_integration.py`, `run_all_tests.py` | TestClient checks of the root and every module's `/health`; a runner that executes each module's `test.py` as a subprocess and summarises. |

### Modules (each a folder under `backend/`, mounted at `/<folder>`)

| Module | Endpoints | Logic |
| --- | --- | --- |
| `signup` | `POST /signup` | Rejects duplicate username/e-mail, stores a bcrypt hash, and seeds a fixed placeholder verification code `123456` for the e-mail |
| `login` | `POST /login` | Matches username and e-mail, verifies the password, returns a bearer JWT and the user profile |
| `email-verify` | `POST /email-verify` | Checks the code for the e-mail, sets `email_verified`, deletes the code |
| `reset-password` | `POST /reset-password` | Same code check, then replaces the password hash |
| `file-parser` | `POST /parse/workspace`, `POST /parse/upload` | Extracts text from txt/md, PDF (`pypdf`) and docx (`python-docx`), using LangChain loaders when installed; uploads are parsed from a temp file and removed |
| `image-parser` | `POST /parse/workspace`, `POST /parse/upload` | Pillow size/format/mode plus EXIF tags; optional vision description through LangChain when a key is set |
| `audio-parser` | `POST /parse/workspace`, `POST /parse/upload` | Duration, sample rate and channels via soundfile or librosa, with a file-size-only fallback |
| `image-creator` | `POST /generate` | Hosted image generation when a key is configured; otherwise a Pillow placeholder whose background colour is derived from a hash of the prompt and which prints the prompt |
| `audio-gen` | `POST /generate` | Hosted text-to-speech when a key is configured; otherwise a standard-library WAV synthesiser that maps character codes to tones (150–550 Hz, 1–8 s) |
| `dod-editor` | `POST /edit` | Natural-language document edits in the workspace through `OpenManusAgent` (creates the file first if allowed) |
| `database-editor` | `GET /tables`, `POST /query`, `/insert`, `/delete` | Raw SQL and simple row operations against the app's SQLite file |
| `cloud` | `GET /files` | Placeholder listing with static sample entries |
| `fileeditor-ai` | `POST /suggest` | Placeholder returning canned editing suggestions |
| `image-editor`, `pdf-editor`, `ppt-editor`, `spreadsheet-editor` | one placeholder action each (`/crop`, `/merge`, `/slide/add`, `/cell/update`) | Return static success payloads; layouts "being finalised" |

Every module also exposes `GET /<module>/health`. Parsers and generators read and write `userfiles/`, which is the per-installation workspace.

### Front end (`templates/`)

One folder per module. `login`, `signup` and `reset-password` contain finished `index.html` pages; the others are empty and are served by the fallback page until designed.

## Setup

Requirements: Python 3.10+. Heavy optional dependencies (LangChain, librosa) are only needed for the corresponding features.

```bash
git clone https://github.com/USER/abrar-cloud.git ~/AbrarCloud
cd ~/AbrarCloud
python -m venv venv && . venv/bin/activate
pip install -r requirements.txt
```

Create `.env` in the project root (read by `backend/config.py`):

```ini
JWT_SECRET_KEY=CHANGE_ME_LONG_RANDOM_STRING
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
HOST=0.0.0.0
PORT=8000
# optional: key for the hosted model provider used by the agent, image creator and speech generator
OPENAI_API_KEY=
```

Several files hard-code the original absolute project path (`router.py` for `templates/`, and each parser/generator for `userfiles/`); change those constants to your checkout location, or run from the same path layout.

## Usage

```bash
cd ~/AbrarCloud
python -m backend.main                 # or: uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

- `GET http://localhost:8000/` → status and registered modules
- `GET http://localhost:8000/backend/router` → template index; `/backend/router/templates/login` → the login page
- Interactive API docs at `/docs`

Example flow:

```bash
curl -s -X POST localhost:8000/signup -H 'content-type: application/json' \
  -d '{"real_name":"Alice","username":"alice","email":"user@example.com","password":"secret"}'
curl -s -X POST localhost:8000/email-verify -H 'content-type: application/json' \
  -d '{"email":"user@example.com","verification_code":"123456"}'
curl -s -X POST localhost:8000/login -H 'content-type: application/json' \
  -d '{"username":"alice","email":"user@example.com","password":"secret"}'
curl -s -X POST localhost:8000/file-parser/parse/upload -F file=@notes.pdf
curl -s -X POST localhost:8000/image-creator/generate -H 'content-type: application/json' \
  -d '{"prompt":"sunset over hills","filename":"sunset.png"}'
```

Tests:

```bash
python backend/run_all_tests.py        # runs every module's test.py and the integration tests
```

## Project structure

```
AbrarCloud/
├── backend/
│   ├── main.py             # app factory, dynamic module loader
│   ├── router.py           # template index and page serving
│   ├── config.py           # settings (.env)
│   ├── database.py         # SQLite schema
│   ├── utils/auth.py       # password hashing, JWT
│   ├── utils/agent.py      # workspace tools + agent with mock fallback
│   ├── <module>/router.py or main.py, test.py   # 17 feature modules
│   ├── test_integration.py
│   └── run_all_tests.py
├── templates/<module>/index.html       # pages (login, signup, reset-password done)
├── Plan/*.md               # per-module blueprints and command history
├── progress.md             # build log
├── requirements.txt
├── userfiles/              # user workspace (runtime data)
└── tasks/                  # reserved for task files
```

## Limitations and notes

- Authentication is minimal: no route is actually protected by the JWT yet, verification codes are a fixed `123456`, and no e-mail is sent. The default JWT secret in `config.py` must be overridden.
- `database-editor` executes arbitrary SQL against the application database with no authorization; keep the server private.
- CORS allows every origin, and the server binds to all interfaces by default.
- Parsers write uploads into `userfiles/` temporarily and the agent fallback writes files there on any instruction containing "write", "edit" or "create".
- Several modules are intentional placeholders returning static data (`cloud`, `fileeditor-ai`, `image-editor`, `pdf-editor`, `ppt-editor`, `spreadsheet-editor`).
- Hard-coded absolute paths must be adjusted when the project is moved.
