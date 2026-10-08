import io
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from markdown_note_taking_app.main import app
from markdown_note_taking_app.routers.notes import (
    get_grammar_checker,
    get_storage_service,
)
from markdown_note_taking_app.services.grammar_service import MockGrammarChecker
from markdown_note_taking_app.services.storage_service import StorageService


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    storage = StorageService(tmp_path)
    mock_grammar = MockGrammarChecker()

    app.dependency_overrides[get_storage_service] = lambda: storage
    app.dependency_overrides[get_grammar_checker] = lambda: mock_grammar

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Markdown Note-taking App"
    assert "/docs" in data["documentation"]


def test_create_note_json(client: TestClient) -> None:
    content = "# Quick Start Guide\n\nContent here."
    response = client.post(
        "/notes",
        json={"filename": "quick-start", "content": content},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "quick-start.md"
    assert data["content"] == content
    assert data["size_bytes"] > 0


def test_create_note_path_traversal_fails(client: TestClient) -> None:
    response = client.post(
        "/notes",
        json={"filename": "../escape", "content": "Bad"},
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


def test_upload_note_file(client: TestClient) -> None:
    file_content = b"# Uploaded Note\n\nThis was uploaded via multipart/form-data."
    files = {"file": ("uploaded_note.md", io.BytesIO(file_content), "text/markdown")}

    response = client.post("/notes/upload", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "uploaded_note.md"
    assert "This was uploaded" in data["content"]


def test_upload_note_invalid_extension(client: TestClient) -> None:
    files = {"file": ("notes.txt", io.BytesIO(b"Hello"), "text/plain")}
    response = client.post("/notes/upload", files=files)
    assert response.status_code == 400
    assert "Only .md files are supported" in response.json()["detail"]


def test_list_and_get_notes(client: TestClient) -> None:
    client.post("/notes", json={"filename": "note1.md", "content": "# 1"})
    client.post("/notes", json={"filename": "note2.md", "content": "# 2"})

    response = client.get("/notes")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    filenames = [n["filename"] for n in data["notes"]]
    assert "note1.md" in filenames
    assert "note2.md" in filenames

    get_resp = client.get("/notes/note1.md")
    assert get_resp.status_code == 200
    assert get_resp.json()["content"] == "# 1"


def test_get_nonexistent_note(client: TestClient) -> None:
    response = client.get("/notes/missing.md")
    assert response.status_code == 404


def test_render_note_html_and_json(client: TestClient) -> None:
    content = "# Heading\n\n**Important** text."
    client.post(
        "/notes",
        json={"filename": "render-test.md", "content": content},
    )

    # HTML format (default)
    html_resp = client.get("/notes/render-test.md/render")
    assert html_resp.status_code == 200
    assert "text/html" in html_resp.headers["content-type"]
    assert "<h1>Heading</h1>" in html_resp.text
    assert "<!DOCTYPE html>" in html_resp.text

    # JSON format
    json_resp = client.get("/notes/render-test.md/render?format=json")
    assert json_resp.status_code == 200
    assert "application/json" in json_resp.headers["content-type"]
    data = json_resp.json()
    assert data["filename"] == "render-test.md"
    assert "<h1>Heading</h1>" in data["html"]


def test_check_text_grammar(client: TestClient) -> None:
    response = client.post(
        "/grammar/check",
        json={"text": "This is teh day we celebrate.", "language": "en-US"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["issue_count"] == 1
    assert data["issues"][0]["replacements"] == ["the"]


def test_check_saved_note_grammar(client: TestClient) -> None:
    content = "I will recieve the package soon."
    client.post(
        "/notes",
        json={"filename": "grammar-note.md", "content": content},
    )

    response = client.post("/notes/grammar-note.md/grammar-check")
    assert response.status_code == 200
    data = response.json()
    assert data["issue_count"] == 1
    assert data["issues"][0]["replacements"] == ["receive"]


def test_check_saved_note_grammar_missing_note(client: TestClient) -> None:
    response = client.post("/notes/missing.md/grammar-check")
    assert response.status_code == 404
