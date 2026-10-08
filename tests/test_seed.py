from pathlib import Path

from markdown_note_taking_app.seed import seed_notes, slugify
from markdown_note_taking_app.services.storage_service import StorageService


def test_slugify() -> None:
    assert slugify("Project Sync: Q3 Plans!") == "project-sync-q3-plans"
    assert slugify("   spaced   name   ") == "spaced-name"
    assert slugify("$$$") == "note"


def test_seed_notes(tmp_path: Path) -> None:
    storage = StorageService(tmp_path)
    created = seed_notes(storage=storage, count=3, clear=False)

    assert len(created) == 3
    notes = storage.list_notes()
    assert len(notes) == 3

    # Check that contents are non-empty markdown
    for name in created:
        detail = storage.get_note(name)
        assert detail.content.startswith("# ")
        assert detail.size_bytes > 0


def test_seed_notes_with_clear(tmp_path: Path) -> None:
    storage = StorageService(tmp_path)
    storage.save_note("old-note.md", "Old content")
    assert len(storage.list_notes()) == 1

    created = seed_notes(storage=storage, count=2, clear=True)
    assert len(created) == 2

    current = storage.list_notes()
    filenames = [n.filename for n in current]
    assert "old-note.md" not in filenames
    assert len(current) == 2
