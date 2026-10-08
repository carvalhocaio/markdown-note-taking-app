import asyncio

import httpx
import pytest

from markdown_note_taking_app.services.grammar_service import (
    LanguageToolHttpClient,
    MockGrammarChecker,
)


def test_mock_grammar_checker_detects_typos() -> None:
    checker = MockGrammarChecker()
    text = "This is teh first test and I will recieve a message untill tomorrow."
    result = asyncio.run(checker.check(text, language="en-US"))

    assert result.issue_count == 3
    rule_replacements = [issue.replacements[0] for issue in result.issues]
    assert "the" in rule_replacements
    assert "receive" in rule_replacements
    assert "until" in rule_replacements


def test_mock_grammar_checker_clean_text() -> None:
    checker = MockGrammarChecker()
    result = asyncio.run(checker.check("A perfectly valid text.", language="en-US"))
    assert result.issue_count == 0
    assert len(result.issues) == 0


def test_language_tool_http_client_parses_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = LanguageToolHttpClient(api_url="http://testserver/v2/check")

    async def mock_post(*args, **kwargs) -> httpx.Response:
        fake_payload = {
            "language": {"code": "en-US"},
            "matches": [
                {
                    "message": "Possible spelling mistake.",
                    "shortMessage": "Spelling",
                    "offset": 5,
                    "length": 3,
                    "replacements": [{"value": "the"}],
                    "rule": {"id": "RULE_123"},
                }
            ],
        }
        return httpx.Response(
            200,
            json=fake_payload,
            request=httpx.Request("POST", "http://testserver/v2/check"),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    result = asyncio.run(client.check("test teh text", language="en-US"))
    assert result.language == "en-US"
    assert result.issue_count == 1
    assert result.issues[0].rule_id == "RULE_123"
    assert result.issues[0].replacements == ["the"]
