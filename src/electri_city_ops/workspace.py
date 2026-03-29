from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from electri_city_ops.models import ActionPlan


@dataclass(slots=True)
class WorkspacePaths:
    root: Path
    database: Path
    json_state_dir: Path
    reports_dir: Path
    rollups_dir: Path
    logs_dir: Path


class WorkspaceGuard:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def resolve_inside(self, candidate: str | Path) -> Path:
        path = Path(candidate)
        resolved = path.resolve() if path.is_absolute() else (self.root / path).resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise ValueError(f"path escapes workspace: {candidate}")
        return resolved

    def ensure_directory(self, candidate: str | Path) -> Path:
        resolved = self.resolve_inside(candidate)
        resolved.mkdir(parents=True, exist_ok=True)
        return resolved

    def ensure_layout(
        self,
        database: Path,
        json_state_dir: Path,
        reports_dir: Path,
        logs_dir: Path,
    ) -> tuple[WorkspacePaths, list[ActionPlan]]:
        actions: list[ActionPlan] = []
        directories = [
            json_state_dir.parent,
            json_state_dir,
            reports_dir,
            reports_dir / "rollups",
            logs_dir,
        ]
        for directory in directories:
            if not directory.exists():
                self.ensure_directory(directory)
                actions.append(
                    ActionPlan(
                        identifier=f"workspace-bootstrap-{directory.name}",
                        phase="apply",
                        scope="workspace",
                        status="applied",
                        description=f"Created workspace directory {directory.relative_to(self.root)}.",
                        target=str(directory),
                        risk="low",
                        reversible=True,
                        requires_approval=False,
                        rollback=f"Remove {directory.relative_to(self.root)} if no longer needed.",
                        validation=f"Directory {directory.relative_to(self.root)} exists.",
                    )
                )
            else:
                self.ensure_directory(directory)
        if not database.parent.exists():
            self.ensure_directory(database.parent)
        return (
            WorkspacePaths(
                root=self.root,
                database=database,
                json_state_dir=json_state_dir,
                reports_dir=reports_dir,
                rollups_dir=reports_dir / "rollups",
                logs_dir=logs_dir,
            ),
            actions,
        )

