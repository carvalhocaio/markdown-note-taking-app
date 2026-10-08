from pathlib import Path

import pytest

from markdown_note_taking_app.services.storage_service import StorageService


def test_save_and_get_note(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    saved = service.save_note("my_note", "# Hello World")

    assert saved.filename == "my_note.md"
    assert saved.content == "# Hello World"
    assert saved.size_bytes > 0

    retrieved = service.get_note("my_note.md")
    assert retrieved.filename == "my_note.md"
    assert retrieved.content == "# Hello World"


def test_save_note_with_extension(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    saved = service.save_note("existing.md", "Content")
    assert saved.filename == "existing.md"

    retrieved = service.get_note("existing")
    assert retrieved.filename == "existing.md"


def test_list_notes(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    service.save_note("note1.md", "Content 1")
    service.save_note("note2.md", "Content 2")

    notes = service.list_notes()
    filenames = [n.filename for n in notes]
    assert len(notes) == 2
    assert "note1.md" in filenames
    assert "note2.md" in filenames


def test_get_nonexistent_note_raises_error(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    with pytest.raises(FileNotFoundError):
        service.get_note("nonexistent.md")


@pytest.mark.parametrize(
    "bad_filename",
    [
        "../secret.md",
        "folder/note.md",
        "..\\windows.md",
        "sub\\note.md",
        "",
        "   ",
    ],
)
def test_path_traversal_and_invalid_filenames_rejected(
    tmp_path: Path, bad_filename: str
) -> None:
    service = StorageService(tmp_path)
    with pytest.raises(ValueError):
        service.save_note(bad_filename, "content")


def test_note_exists(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    assert not service.note_exists("test.md")
    service.save_note("test.md", "hello")
    assert service.note_exists("test.md")
    assert not service.note_exists("../bad.md")


def test_delete_note(tmp_path: Path) -> None:
    service = StorageService(tmp_path)
    service.save_note("to_delete.md", "bye")
    assert service.note_exists("to_delete.md")

    service.delete_note("to_delete.md")
    assert not service.note_exists("to_delete.md")

    with pytest.raises(FileNotFoundError):
        service.delete_note("to_delete.md")
