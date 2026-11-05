import pandas as pd
import pytest

from backend.app.main import PipelineRunner
from backend.app.services.evaluation import EvaluationService
from backend.app.services.ingestion import IngestionService
from backend.app.services.registry import RegistryResult, RegistryService
from backend.app.services.training import TrainingService
from backend.app.services.validation import ValidationService
from pipeline_schema.models import (
    DatasetNodeConfig,
    Edge,
    EvaluationNodeConfig,
    PipelineConfig,
    RegistryNodeConfig,
    TrainingNodeConfig,
    ValidationNodeConfig,
)


class FakeModelRegistry:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def log_and_register(self, model, model_name, stage, metric_name, metric_value):
        self.calls.append({"model_name": model_name, "stage": stage, "metric_value": metric_value})
        return RegistryResult(registered=True, model_name=model_name, version="1", run_id="fake-run")


@pytest.fixture
def sample_dataset_path(tmp_path):
    df = pd.DataFrame({
        "x1": [0.1, 0.5, -0.3, 0.8, -0.9, 0.2, 0.4, -0.6, 0.7, -0.1],
        "x2": [0.2, 0.1, -0.1, 0.3, -0.4, 0.5, 0.1, -0.2, 0.6, -0.3],
        "label": [1, 1, 0, 1, 0, 1, 1, 0, 1, 0],
    })
    path = tmp_path / "sample.csv"
    df.to_csv(path, index=False)
    return str(path)


def build_pipeline_config(dataset_path: str, threshold: float = 0.0) -> PipelineConfig:
    return PipelineConfig(
        pipeline_id="test_pipeline",
        name="Test Pipeline",
        nodes=[
            DatasetNodeConfig(id="n1", name="Dataset", source_path=dataset_path, target_column="label", test_size=0.3),
            ValidationNodeConfig(id="n2", name="Validation", required_columns=["x1", "x2", "label"]),
            TrainingNodeConfig(id="n3", name="Training", algorithm="random_forest_classifier", hyperparameters={"n_estimators": 10}),
            EvaluationNodeConfig(id="n4", name="Evaluation", metric="accuracy", threshold=threshold),
            RegistryNodeConfig(id="n5", name="Registry", model_name="test_model"),
        ],
        edges=[
            Edge(source="n1", target="n2"),
            Edge(source="n2", target="n3"),
            Edge(source="n3", target="n4"),
            Edge(source="n4", target="n5"),
        ],
    )


@pytest.fixture
def runner_with_fake_registry():
    fake_registry = FakeModelRegistry()
    runner = PipelineRunner(
        ingestion=IngestionService(),
        validation=ValidationService(),
        training=TrainingService(),
        evaluation=EvaluationService(),
        registry=RegistryService(fake_registry),
    )
    return runner, fake_registry


def test_pipeline_registers_model_when_evaluation_passes(sample_dataset_path, runner_with_fake_registry):
    runner, fake_registry = runner_with_fake_registry
    config = build_pipeline_config(sample_dataset_path, threshold=0.0)

    result = runner.run(config)

    assert result.stopped_at is None
    assert result.evaluation.passed is True
    assert result.registry.registered is True
    assert len(fake_registry.calls) == 1


def test_pipeline_skips_registry_when_evaluation_fails(sample_dataset_path, runner_with_fake_registry):
    runner, fake_registry = runner_with_fake_registry
    config = build_pipeline_config(sample_dataset_path, threshold=1.1)  # accuracy can never clear this

    result = runner.run(config)

    assert result.evaluation.passed is False
    assert result.registry.registered is False
    assert fake_registry.calls == []


def test_pipeline_stops_at_validation_when_required_column_missing(sample_dataset_path, runner_with_fake_registry):
    runner, _ = runner_with_fake_registry
    config = build_pipeline_config(sample_dataset_path)
    config.nodes[1].required_columns = ["x1", "x2", "label", "missing_column"]

    result = runner.run(config)

    assert result.stopped_at == "n2"
    assert result.training is None