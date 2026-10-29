"""Structured output contracts for specialized agents."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnalysisOutput(BaseModel):
    """Structured findings produced by the analysis agent."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=2000)
    findings: list[str] = Field(min_length=1, max_length=30)
    recommendations: list[str] = Field(default_factory=list, max_length=20)

    @field_validator("summary")
    @classmethod
    def normalize_summary(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Analysis summary cannot be blank.")
        return normalized


class ReportSection(BaseModel):
    """A section in a generated report."""

    model_config = ConfigDict(extra="forbid")

    heading: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=10_000)


class ReportOutput(BaseModel):
    """Structured report produced by the report agent."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    executive_summary: str = Field(min_length=1, max_length=2000)
    sections: list[ReportSection] = Field(min_length=1, max_length=20)
    conclusion: str = Field(min_length=1, max_length=2000)
