"""RFC 7807 problem+json models (ROADMAP-005)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ProblemDetails(BaseModel):
    """RFC 7807 Problem Details document.

    See https://datatracker.ietf.org/doc/html/rfc7807
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    type: str = Field(
        default="about:blank",
        description="Problem type URI.",
    )
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    request_id: str | None = None

    def to_response_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable dict excluding unset optionals."""
        return self.model_dump(mode="json", exclude_none=True)
