# Markdown Note-taking App

A RESTful API note-taking backend built with **FastAPI** and **Python 3.12+**, based on the [roadmap.sh Markdown Note-taking App](https://roadmap.sh/projects/markdown-note-taking-app) challenge.

## Features

- **Save notes via JSON:** Create and save notes directly passing Markdown strings.
- **Upload markdown files:** Multipart file upload (`.md`) with automatic UTF-8 validation and safe storage.
- **List saved notes:** Inspect all saved markdown notes with metadata (filename, size in bytes, last modified date).
- **Retrieve raw notes:** View original markdown content.
- **Render markdown to HTML:** Convert Markdown notes into styled HTML for direct browser viewing or JSON structured responses.
- **Check grammar:** Integrated with the official LanguageTool API (`https://api.languagetool.org/v2/check`) with fallback mock support for offline testing. Supports checking arbitrary text or existing saved notes.
- **Security:** Built-in path traversal protection ensuring files cannot escape the designated storage directory.

---

## Getting Started

### Prerequisites

- [uv](https://github.com/astral-sh/uv) (package and virtual environment manager)
- Python 3.12+

### Installation

```bash
make sync
```

### Running the Development Server

```bash
uv run uvicorn markdown_note_taking_app.main:app --reload
```

### Seeding Sample Notes

Generate realistic sample Markdown notes using **Faker**:

```bash
make seed            # Generates 5 sample notes
make seed COUNT=10   # Generates 10 sample notes
```

Interactive OpenAPI documentation is available at:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

---

## API Endpoints

### 1. Save Note (JSON)

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Content-Type: application/json" \
  -d '{"filename": "my-note", "content": "# My Note\n\nThis is a markdown note."}'
```

### 2. Upload Note (.md file)

```bash
curl -X POST http://127.0.0.1:8000/notes/upload \
  -F "file=@/path/to/sample.md"
```

### 3. List Saved Notes

```bash
curl http://127.0.0.1:8000/notes
```

### 4. Get Note Details

```bash
curl http://127.0.0.1:8000/notes/my-note.md
```

### 5. Render Note in HTML

- **View in browser (HTML):**
  ```bash
  curl http://127.0.0.1:8000/notes/my-note.md/render
  ```
- **As JSON payload:**
  ```bash
  curl http://127.0.0.1:8000/notes/my-note.md/render?format=json
  ```

### 6. Grammar Checking

- **Check arbitrary text:**
  ```bash
  curl -X POST http://127.0.0.1:8000/grammar/check \
    -H "Content-Type: application/json" \
    -d '{"text": "This is teh test text.", "language": "en-US"}'
  ```

- **Check saved note:**
  ```bash
  curl -X POST "http://127.0.0.1:8000/notes/my-note.md/grammar-check?language=en-US"
  ```

---

## Quality and Verification

```bash
make ci        # Run full pipeline: lint, format-check, typecheck, audit, test
make test      # Run pytest test suite
make lint      # Check code with ruff
make format    # Format code with ruff
make typecheck # Run Pyright static type checking
```
