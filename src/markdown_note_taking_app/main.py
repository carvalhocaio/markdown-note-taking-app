from fastapi import FastAPI

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


@app.get("/", summary="API Root Information")
def read_root() -> dict[str, str]:
    return {
        "name": "Markdown Note-taking App",
        "version": __version__,
        "documentation": "/docs",
    }
