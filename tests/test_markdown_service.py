from markdown_note_taking_app.services.markdown_service import MarkdownService


def test_render_fragment() -> None:
    service = MarkdownService()
    content = "# Title\n\nThis is **bold** and *italic*."
    html = service.render_fragment(content)

    assert "<h1>Title</h1>" in html
    assert "<strong>bold</strong>" in html
    assert "<em>italic</em>" in html


def test_render_page() -> None:
    service = MarkdownService()
    content = "## Subtitle\n\n- item 1\n- item 2"
    page = service.render_page("notes.md", content)

    assert "<!DOCTYPE html>" in page
    assert "<title>notes</title>" in page
    assert "<h2>Subtitle</h2>" in page
    assert "<li>item 1</li>" in page
    assert "<li>item 2</li>" in page
