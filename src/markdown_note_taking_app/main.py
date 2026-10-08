from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

from markdown_note_taking_app import __version__
from markdown_note_taking_app.routers.notes import router as notes_router

app = FastAPI(
    title="Markdown Note-taking App",
    description=(
        "A RESTful API for taking notes in Markdown, "
        "checking grammar, and rendering to HTML."
    ),
    version=__version__,
)

app.include_router(notes_router)

STATIC_DIR = Path(__file__).parent / "static"
STATIC_INDEX = STATIC_DIR / "index.html"
STATIC_FAVICON = STATIC_DIR / "favicon.svg"


@app.get("/", summary="Web Interface and API Root", response_model=None)
def read_root(request: Request) -> Any:
    """Serve the Web Interface for browsers or API metadata for JSON clients."""
    accept = request.headers.get("accept", "")

    # If accessed by a browser requesting HTML
    if (
        "text/html" in accept
        and "application/json" not in accept
        and STATIC_INDEX.is_file()
    ):
        return HTMLResponse(
            content=STATIC_INDEX.read_text(encoding="utf-8"),
            media_type="text/html",
        )

    return JSONResponse(
        content={
            "name": "Markdown Note-taking App",
            "version": __version__,
            "documentation": "/docs",
            "ui": "/app",
        }
    )


@app.get("/app", response_class=HTMLResponse, include_in_schema=False)
def read_app() -> HTMLResponse:
    """Serve the Web Interface directly."""
    if STATIC_INDEX.is_file():
        return HTMLResponse(
            content=STATIC_INDEX.read_text(encoding="utf-8"),
            media_type="text/html",
        )
    return HTMLResponse(content="<h1>Interface not found</h1>", status_code=404)


@app.get("/favicon.ico", include_in_schema=False)
def get_favicon() -> Response:
    """Serve the application favicon."""
    if STATIC_FAVICON.is_file():
        return Response(
            content=STATIC_FAVICON.read_bytes(),
            media_type="image/svg+xml",
        )
    return Response(status_code=404)
