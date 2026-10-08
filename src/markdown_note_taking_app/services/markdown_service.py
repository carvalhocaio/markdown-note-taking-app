from markdown_it import MarkdownIt


class MarkdownService:
    """Service to convert Markdown content into rendered HTML."""

    def __init__(self) -> None:
        self.md = MarkdownIt("commonmark", {"breaks": True, "html": False})

    def render_fragment(self, content: str) -> str:
        """Render raw Markdown text into an HTML fragment."""
        return self.md.render(content)

    def render_page(self, filename: str, content: str) -> str:
        """Render Markdown text into a complete, styled HTML document."""
        fragment = self.render_fragment(content)
        title = filename.removesuffix(".md")

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #e2e8f0;
      --heading: #f8fafc;
      --border: #334155;
      --link: #38bdf8;
      --code-bg: #0f172a;
    }}
    @media (prefers-color-scheme: light) {{
      :root {{
        --bg: #f8fafc;
        --card-bg: #ffffff;
        --text: #334155;
        --heading: #0f172a;
        --border: #e2e8f0;
        --link: #0284c7;
        --code-bg: #f1f5f9;
      }}
    }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
        Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      background-color: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 2rem 1rem;
      display: flex;
      justify-content: center;
    }}
    main {{
      max-width: 800px;
      width: 100%;
      background: var(--card-bg);
      padding: 2.5rem;
      border-radius: 12px;
      border: 1px solid var(--border);
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }}
    h1, h2, h3, h4, h5, h6 {{
      color: var(--heading);
      margin-top: 1.5em;
      margin-bottom: 0.5em;
      line-height: 1.25;
    }}
    h1 {{
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.3em;
      margin-top: 0;
    }}
    a {{ color: var(--link); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code {{
      background: var(--code-bg);
      padding: 0.2em 0.4em;
      border-radius: 4px;
      font-size: 85%;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }}
    pre {{
      background: var(--code-bg);
      padding: 1rem;
      border-radius: 8px;
      overflow-x: auto;
      border: 1px solid var(--border);
    }}
    pre code {{ padding: 0; background: transparent; }}
    blockquote {{
      margin: 1rem 0;
      padding-left: 1rem;
      border-left: 4px solid var(--border);
      color: var(--text);
      opacity: 0.85;
    }}
    ul, ol {{ padding-left: 2rem; }}
    hr {{ border: none; border-top: 1px solid var(--border); margin: 2rem 0; }}
  </style>
</head>
<body>
  <main>
    {fragment}
  </main>
</body>
</html>"""
