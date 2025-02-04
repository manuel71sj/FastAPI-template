from typing import Optional

from pydantic import BaseModel


class RedisValueDTO(BaseModel):
    """DTO for redis values."""

    key: str
    value: str | None  # noqa: WPS110
