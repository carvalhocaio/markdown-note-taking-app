from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import HTMLResponse

from markdown_note_taking_app.config import settings
from markdown_note_taking_app.schemas import (
    GrammarCheckRequest,
    GrammarCheckResponse,
    NoteCreateRequest,
    NoteDetailResponse,
    NoteListResponse,
    NoteRenderResponse,
)
from markdown_note_taking_app.services.grammar_service import (
    GrammarChecker,
    get_grammar_checker,
)
from markdown_note_taking_app.services.markdown_service import MarkdownService
from markdown_note_taking_app.services.storage_service import StorageService

router = APIRouter(tags=["notes"])


def get_storage_service() -> StorageService:
    return StorageService(settings.storage_dir)


def get_markdown_service() -> MarkdownService:
    return MarkdownService()


@router.post(
    "/notes",
    response_model=NoteDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a markdown note from JSON payload",
)
def create_note(
    payload: NoteCreateRequest,
    storage: Annotated[StorageService, Depends(get_storage_service)],
) -> NoteDetailResponse:
    try:
        return storage.save_note(payload.filename, payload.content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/notes/upload",
    response_model=NoteDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a markdown note from uploaded .md file",
)
async def upload_note(
    file: Annotated[
        UploadFile,
        File(description="Markdown (.md) file to upload"),
    ],
    storage: Annotated[StorageService, Depends(get_storage_service)],
) -> NoteDetailResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    if not file.filename.lower().endswith(".md"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .md files are supported for upload",
        )

    try:
        raw_bytes = await file.read()
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must be valid UTF-8 encoded text",
        ) from exc

    try:
        return storage.save_note(file.filename, content)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/notes",
    response_model=NoteListResponse,
    summary="List all saved markdown notes",
)
def list_notes(
    storage: Annotated[StorageService, Depends(get_storage_service)],
) -> NoteListResponse:
    notes = storage.list_notes()
    return NoteListResponse(notes=notes, total=len(notes))


@router.get(
    "/notes/{filename}",
    response_model=NoteDetailResponse,
    summary="Get raw markdown note content and metadata",
)
def get_note(
    filename: str,
    storage: Annotated[StorageService, Depends(get_storage_service)],
) -> NoteDetailResponse:
    try:
        return storage.get_note(filename)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.delete(
    "/notes/{filename}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a markdown note",
)
def delete_note(
    filename: str,
    storage: Annotated[StorageService, Depends(get_storage_service)],
) -> None:
    try:
        storage.delete_note(filename)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/notes/{filename}/render",
    response_model=None,
    summary="Render a markdown note as HTML or JSON",
    responses={
        200: {
            "content": {
                "text/html": {},
                "application/json": {},
            },
            "description": "Rendered note content",
        }
    },
)
def render_note(
    filename: str,
    storage: Annotated[StorageService, Depends(get_storage_service)],
    markdown: Annotated[MarkdownService, Depends(get_markdown_service)],
    format: Annotated[
        Literal["html", "json"],
        Query(description="Output format: 'html' for browser view or 'json'"),
    ] = "html",
) -> HTMLResponse | NoteRenderResponse:
    try:
        note = storage.get_note(filename)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if format == "json":
        html_fragment = markdown.render_fragment(note.content)
        return NoteRenderResponse(filename=note.filename, html=html_fragment)

    html_page = markdown.render_page(note.filename, note.content)
    return HTMLResponse(content=html_page, media_type="text/html")


@router.post(
    "/notes/{filename}/grammar-check",
    response_model=GrammarCheckResponse,
    summary="Check grammar of a saved markdown note",
)
async def check_note_grammar(
    filename: str,
    storage: Annotated[StorageService, Depends(get_storage_service)],
    grammar: Annotated[GrammarChecker, Depends(get_grammar_checker)],
    language: Annotated[
        str,
        Query(description="Language code (e.g. en-US, pt-BR)"),
    ] = "en-US",
) -> GrammarCheckResponse:
    try:
        note = storage.get_note(filename)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    try:
        return await grammar.check(note.content, language=language)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc


@router.post(
    "/grammar/check",
    response_model=GrammarCheckResponse,
    summary="Check grammar of arbitrary text",
)
async def check_text_grammar(
    payload: GrammarCheckRequest,
    grammar: Annotated[GrammarChecker, Depends(get_grammar_checker)],
) -> GrammarCheckResponse:
    try:
        return await grammar.check(payload.text, language=payload.language)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
