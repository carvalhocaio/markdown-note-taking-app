from datetime import UTC, datetime
from pathlib import Path

from markdown_note_taking_app.schemas import (
    NoteDetailResponse,
    NoteMetadataResponse,
)


class StorageService:
    """Service for safely managing markdown notes on the filesystem."""

    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir.resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_and_resolve(self, raw_filename: str) -> tuple[str, Path]:
        clean_name = raw_filename.strip()
        if not clean_name:
            raise ValueError("Filename cannot be empty")

        if "/" in clean_name or "\\" in clean_name or ".." in clean_name:
            raise ValueError(
                "Path separators and parent directory references ('..') are not allowed"
            )

        if not clean_name.lower().endswith(".md"):
            clean_name = f"{clean_name}.md"

        target_path = (self.base_dir / clean_name).resolve()

        if not target_path.is_relative_to(self.base_dir):
            raise ValueError("Path traversal detected")

        return clean_name, target_path

    def save_note(self, filename: str, content: str) -> NoteDetailResponse:
        sanitized_name, target_path = self._sanitize_and_resolve(filename)
        target_path.write_text(content, encoding="utf-8")

        stat = target_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

        return NoteDetailResponse(
            filename=sanitized_name,
            content=content,
            size_bytes=stat.st_size,
            modified_at=modified_at,
        )

    def get_note(self, filename: str) -> NoteDetailResponse:
        sanitized_name, target_path = self._sanitize_and_resolve(filename)
        if not target_path.is_file():
            raise FileNotFoundError(f"Note '{sanitized_name}' not found")

        content = target_path.read_text(encoding="utf-8")
        stat = target_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)

        return NoteDetailResponse(
            filename=sanitized_name,
            content=content,
            size_bytes=stat.st_size,
            modified_at=modified_at,
        )

    def list_notes(self) -> list[NoteMetadataResponse]:
        notes: list[NoteMetadataResponse] = []
        for file_path in self.base_dir.glob("*.md"):
            if file_path.is_file():
                stat = file_path.stat()
                modified_at = datetime.fromtimestamp(stat.st_mtime, tz=UTC)
                notes.append(
                    NoteMetadataResponse(
                        filename=file_path.name,
                        size_bytes=stat.st_size,
                        modified_at=modified_at,
                    )
                )

        notes.sort(key=lambda n: n.modified_at, reverse=True)
        return notes

    def note_exists(self, filename: str) -> bool:
        try:
            _, target_path = self._sanitize_and_resolve(filename)
            return target_path.is_file()
        except ValueError:
            return False
