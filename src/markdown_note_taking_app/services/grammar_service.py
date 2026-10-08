from typing import Any, ClassVar, Protocol

import httpx

from markdown_note_taking_app.config import settings
from markdown_note_taking_app.schemas import GrammarCheckResponse, GrammarIssue


class GrammarChecker(Protocol):
    """Protocol for grammar checking implementations."""

    async def check(self, text: str, language: str = "en-US") -> GrammarCheckResponse:
        """Check text for grammar and spelling errors."""
        ...


class LanguageToolHttpClient:
    """Grammar checker using the official LanguageTool HTTP REST API."""

    def __init__(
        self,
        api_url: str | None = None,
        timeout: float | None = None,
    ) -> None:
        self.api_url = api_url or settings.languagetool_url
        self.timeout = timeout or settings.languagetool_timeout

    async def check(self, text: str, language: str = "en-US") -> GrammarCheckResponse:
        payload = {
            "text": text,
            "language": language,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(self.api_url, data=payload)
                response.raise_for_status()
                data: dict[str, Any] = response.json()
            except httpx.HTTPError as exc:
                raise RuntimeError(f"LanguageTool API request failed: {exc}") from exc

        matches = data.get("matches", [])
        issues: list[GrammarIssue] = []

        for match in matches:
            replacements: list[str] = [
                rep["value"]
                for rep in match.get("replacements", [])
                if isinstance(rep, dict) and isinstance(rep.get("value"), str)
            ]
            rule = match.get("rule", {})
            rule_id = rule.get("id") if isinstance(rule, dict) else None

            issues.append(
                GrammarIssue(
                    message=match.get("message", "Grammar issue detected"),
                    short_message=match.get("shortMessage"),
                    offset=match.get("offset", 0),
                    length=match.get("length", 0),
                    replacements=replacements,
                    rule_id=rule_id,
                )
            )

        detected_lang = (
            data.get("language", {}).get("code")
            if isinstance(data.get("language"), dict)
            else language
        )

        return GrammarCheckResponse(
            language=detected_lang or language,
            issues=issues,
            issue_count=len(issues),
        )


class MockGrammarChecker:
    """In-memory deterministic grammar checker for testing without network requests."""

    KNOWN_TYPOS: ClassVar[dict[str, str]] = {
        "teh": "the",
        "recieve": "receive",
        "seperate": "separate",
        "occured": "occurred",
        "untill": "until",
    }

    async def check(self, text: str, language: str = "en-US") -> GrammarCheckResponse:
        issues: list[GrammarIssue] = []

        words = text.split()
        current_offset = 0

        for word in words:
            clean_word = word.strip(".,!?;:\"'()[]{}").lower()
            offset = text.find(word, current_offset)
            if offset != -1:
                current_offset = offset + len(word)

            if clean_word in self.KNOWN_TYPOS:
                replacement = self.KNOWN_TYPOS[clean_word]
                issues.append(
                    GrammarIssue(
                        message=(
                            f"Possible spelling mistake. Did you mean '{replacement}'?"
                        ),
                        short_message="Spelling mistake",
                        offset=offset if offset != -1 else 0,
                        length=len(word),
                        replacements=[replacement],
                        rule_id="MOCK_SPELLING_RULE",
                    )
                )

        return GrammarCheckResponse(
            language=language,
            issues=issues,
            issue_count=len(issues),
        )


def get_grammar_checker() -> GrammarChecker:
    """Dependency provider for FastAPI."""
    if settings.use_mock_grammar:
        return MockGrammarChecker()
    return LanguageToolHttpClient()
