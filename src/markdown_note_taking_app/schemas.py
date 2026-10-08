from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreateRequest(BaseModel):
    filename: str = Field(
        ...,
        min_length=1,
        description="Filename for the note (with or without .md)",
    )
    content: str = Field(..., description="Markdown text content of the note")


class NoteMetadataResponse(BaseModel):
    filename: str
    size_bytes: int
    modified_at: datetime


class NoteDetailResponse(BaseModel):
    filename: str
    content: str
    size_bytes: int
    modified_at: datetime


class NoteListResponse(BaseModel):
    notes: list[NoteMetadataResponse]
    total: int


class NoteRenderResponse(BaseModel):
    filename: str
    html: str


class GrammarCheckRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Text to be checked for grammar and spelling",
    )
    language: str = Field(
        default="en-US",
        description="Language code (e.g. en-US, pt-BR)",
    )


class GrammarIssue(BaseModel):
    message: str
    short_message: str | None = None
    offset: int
    length: int
    replacements: list[str] = Field(default_factory=list)
    rule_id: str | None = None


class GrammarCheckResponse(BaseModel):
    language: str
    issues: list[GrammarIssue]
    issue_count: int
