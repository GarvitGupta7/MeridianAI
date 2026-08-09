from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[2])
    random_state: int = 42
    min_clusters: int = 2
    max_clusters: int = 8

    @property
    def artifacts_dir(self) -> Path:
        path = self.project_root / "artifacts"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def database_path(self) -> Path:
        return self.artifacts_dir / "retail_segmentation.db"


settings = Settings()

