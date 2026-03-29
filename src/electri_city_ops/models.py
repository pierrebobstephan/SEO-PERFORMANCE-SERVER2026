from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha1
from typing import Any


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def stable_fingerprint(*parts: str) -> str:
    material = "||".join(part.strip() for part in parts if part).encode("utf-8")
    return sha1(material).hexdigest()


@dataclass(slots=True)
class Metric:
    name: str
    value: float
    unit: str = ""
    scope: str = "system"
    source: str = "system"


@dataclass(slots=True)
class Finding:
    category: str
    severity: str
    title: str
    detail: str
    risk: str
    confidence: float
    source: str
    target: str
    recommendation: str
    fingerprint: str = ""
    priority_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.fingerprint:
            self.fingerprint = stable_fingerprint(self.category, self.target, self.title)


@dataclass(slots=True)
class ActionPlan:
    identifier: str
    phase: str
    scope: str
    status: str
    description: str
    target: str
    risk: str
    reversible: bool
    requires_approval: bool
    rollback: str
    validation: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationCheck:
    name: str
    success: bool
    detail: str


@dataclass(slots=True)
class LearningNote:
    title: str
    detail: str
    source: str = "learning"


@dataclass(slots=True)
class TargetSnapshot:
    domain: str
    final_url: str
    homepage_status_code: int
    response_ms: float
    html_bytes: int
    content_encoding: str
    cache_control: str
    title: str
    meta_description: str
    canonical: str
    h1_count: int
    html_lang: str
    viewport_present: bool
    robots_meta: str
    sitemap_status_code: int
    fetch_error: str = ""


@dataclass(slots=True)
class CycleResult:
    run_id: str
    started_at: str
    finished_at: str
    mode: str
    status: str
    target_results: list[TargetSnapshot] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    metrics: list[Metric] = field(default_factory=list)
    actions: list[ActionPlan] = field(default_factory=list)
    validations: list[ValidationCheck] = field(default_factory=list)
    learning_notes: list[LearningNote] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "mode": self.mode,
            "status": self.status,
            "target_results": [asdict(item) for item in self.target_results],
            "findings": [asdict(item) for item in self.findings],
            "metrics": [asdict(item) for item in self.metrics],
            "actions": [asdict(item) for item in self.actions],
            "validations": [asdict(item) for item in self.validations],
            "learning_notes": [asdict(item) for item in self.learning_notes],
            "summary": self.summary,
        }
