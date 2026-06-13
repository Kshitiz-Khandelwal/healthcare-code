from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = PROJECT_DIR.parents[1]


@dataclass(frozen=True)
class PipelineConfig:
    # Change only this value when moving from the validated B0 prototype to B4.
    active_profile: str = "production"
    seed: int = 42
    sampling_frequency: int = 500
    lead_indices: tuple[int, int, int] = (0, 1, 10)
    lead_names: tuple[str, str, str] = ("I", "II", "V5")
    wavelet: str = "cmor1.5-1.0"
    min_frequency_hz: float = 0.5
    max_frequency_hz: float = 40.0
    cwt_frequencies: int = 128
    checkpoint_every: int = 25
    cv_folds: int = 3
    pca_components: int = 30
    n_estimators: int = 150
    n_jobs: int = 1
    test_size: float = 0.20

    # Phase 1 smoke-test configuration.
    prototype_model_name: str = "efficientnet_b0"
    prototype_max_records: int = 300
    prototype_target_size: tuple[int, int] = (224, 224)
    prototype_embedding_dim: int = 1280

    # Phase 2 production configuration. Execution is guarded by Phase 1.
    production_model_name: str = "efficientnet_b4"
    production_max_records: int = 1000
    production_target_size: tuple[int, int] = (380, 380)
    production_embedding_dim: int = 1792

    @property
    def active_model_name(self) -> str:
        if self.active_profile == "prototype":
            return self.prototype_model_name
        if self.active_profile == "production":
            return self.production_model_name
        raise ValueError(f"Unsupported active profile: {self.active_profile}")

    @property
    def active_max_records(self) -> int:
        if self.active_profile == "prototype":
            return self.prototype_max_records
        if self.active_profile == "production":
            return self.production_max_records
        raise ValueError(f"Unsupported active profile: {self.active_profile}")

    @property
    def raw_dataset_dir(self) -> Path:
        return (
            WORKSPACE_DIR
            / "Jennie mams thing finally staritng"
            / "Dataset"
            / "WFDBRecords"
        )

    @property
    def handcrafted_dataset_path(self) -> Path:
        return PROJECT_DIR / "ecg_dataset.csv"

    @property
    def output_dir(self) -> Path:
        return PROJECT_DIR / "outputs" / "deep_features"

    @property
    def manifest_dir(self) -> Path:
        return self.output_dir / "manifests"

    @property
    def embedding_dir(self) -> Path:
        return self.output_dir / "embeddings"

    @property
    def feature_dir(self) -> Path:
        return self.output_dir / "features"

    @property
    def result_dir(self) -> Path:
        return self.output_dir / "results"

    @property
    def model_dir(self) -> Path:
        return self.output_dir / "models"

    @property
    def log_dir(self) -> Path:
        return PROJECT_DIR / "logs"

    @property
    def test_dir(self) -> Path:
        return PROJECT_DIR / "tests"

    def ensure_directories(self) -> None:
        for path in (
            self.output_dir,
            self.manifest_dir,
            self.embedding_dir,
            self.feature_dir,
            self.result_dir,
            self.model_dir,
            self.log_dir,
            self.test_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)

    def model_target_size(self, model_name: str) -> tuple[int, int]:
        if model_name == self.prototype_model_name:
            return self.prototype_target_size
        if model_name == self.production_model_name:
            return self.production_target_size
        raise ValueError(f"Unsupported model name: {model_name}")

    def model_embedding_dim(self, model_name: str) -> int:
        if model_name == self.prototype_model_name:
            return self.prototype_embedding_dim
        if model_name == self.production_model_name:
            return self.production_embedding_dim
        raise ValueError(f"Unsupported model name: {model_name}")

    def scalogram_dir(self, model_name: str) -> Path:
        width, height = self.model_target_size(model_name)
        suffix = str(width) if width == height else f"{width}x{height}"
        return self.output_dir / f"scalograms_3ch_{suffix}"

    def scalogram_manifest_path(self, model_name: str) -> Path:
        width, height = self.model_target_size(model_name)
        suffix = str(width) if width == height else f"{width}x{height}"
        return self.manifest_dir / f"scalogram_manifest_3ch_{suffix}.csv"

    def embedding_manifest_path(self, model_name: str) -> Path:
        return self.manifest_dir / f"{model_name}_embedding_manifest.csv"

    def deep_feature_path(self, model_name: str) -> Path:
        return self.feature_dir / f"{model_name}_deep_features.csv"

    def hybrid_feature_path(self, model_name: str) -> Path:
        return self.feature_dir / f"hybrid_handcrafted_{model_name}.csv"

    def model_artifact_path(self, model_name: str) -> Path:
        return self.model_dir / f"best_hybrid_model_{model_name}.pkl"

    def feature_list_path(self, model_name: str) -> Path:
        return self.model_dir / f"best_hybrid_feature_list_{model_name}.pkl"

    def scaler_path(self, model_name: str) -> Path:
        return self.model_dir / f"scaler_{model_name}.pkl"

    def pca_path(self, model_name: str) -> Path:
        return self.model_dir / f"pca_{model_name}.pkl"

    def metadata_path(self, model_name: str) -> Path:
        return self.model_dir / f"model_metadata_{model_name}.json"


CONFIG = PipelineConfig()
CONFIG.ensure_directories()
