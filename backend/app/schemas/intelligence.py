from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class RecommendationItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    priority: Literal["high", "medium", "low"]
    title: str = Field(min_length=3, max_length=180)
    reason: str = Field(min_length=3, max_length=500)
    steps: list[str] = Field(min_length=1, max_length=8)

class RecommendationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[RecommendationItem] = Field(min_length=1, max_length=12)
