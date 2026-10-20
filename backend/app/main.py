from __future__ import annotations
from dataclasses import dataclass,field
from typing import Any,Callable
from fastapi import FastAPI,HTTPException
from sklearn.base import BaseEstimator
from backend.app.services.evaluation import EvaluationResult, EvaluationService
from backend.app.services.ingestion import IngestionResult, IngestionService
from backend.app.services.registry import MlflowModelRegistry, RegistryResult, RegistryService
from backend.app.services.training import TrainingResult, TrainingService
from backend.app.services.validation import ValidationService
from pipeline_schema.models import (
    DatasetNodeConfig,
    EvaluationNodeConfig,
    NodeConfig,
    NodeType,
    PipelineConfig,
    RegistryNodeConfig,
    TrainingNodeConfig,
    ValidationNodeConfig
)
from pipeline_schema.validators import ValidationReport
from fastapi.middleware.cors import CORSMiddleware



MLFLOW_TRACING_URI="http://localhost:5000"

@dataclass
class PipelineRunResult:
    pipeline_id: str
    model: BaseEstimator | None = None
    ingestion: IngestionResult | None = None
    validation: ValidationReport | None = None
    training: TrainingResult | None = None
    evaluation: EvaluationResult | None = None
    registry: RegistryResult | None = None
    stopped_at: str | None = None
    errors: list[str] = field(default_factory=list)


class PipelineRunner:
    
    def __init__(
        self,
        ingestion: IngestionService,
        validation: ValidationService,
        training: TrainingService,
        evaluation: EvaluationService,
        registry: RegistryService
        )-> None:
        self.ingestion = ingestion
        self.validation = validation
        self.training = training
        self.evaluation = evaluation
        self.registry = registry
        self._handlers: dict[NodeType, Callable[[NodeConfig, PipelineRunResult], bool]] = {
            NodeType.DATASET: self._handle_dataset,
            NodeType.VALIDATION: self._handle_validation,
            NodeType.TRAINING: self._handle_training,
            NodeType.EVALUATION: self._handle_evaluation,
            NodeType.REGISTRY: self._handle_registry,
        }
    
    def run(self,config:PipelineConfig) -> PipelineRunResult:
        result = PipelineRunResult(pipeline_id=config.pipeline_id)
        
        for node in config.topological_order():
            should_continue = self._handlers[node.type](node,result)
            if not should_continue:
                break
        
        return result
    
    def _handle_dataset(self,node:NodeConfig,result:PipelineRunResult) -> bool:
        assert isinstance( node, DatasetNodeConfig)
        result.ingestion = self.ingestion.run(node)
        return True
    
    def _handle_validation(self, node:NodeConfig,result:PipelineRunResult) -> bool:
        assert isinstance(node,ValidationNodeConfig)
        result.validation=self.validation.run(node,result.ingestion)
        if not result.validation.passed:
            result.stopped_at=node.id
            result.errors.append("validation check failed")
            return False
        return True
    
    def _handle_training(self,node:NodeConfig,result:PipelineRunResult) -> bool:
        assert isinstance(node,TrainingNodeConfig)
        result.training = self.training.run(node,result.ingestion)
        result.model = result.training.model
        return True
    
    def _handle_evaluation(self, node: NodeConfig, result: PipelineRunResult) -> bool:
        assert isinstance(node, EvaluationNodeConfig)
        result.evaluation = self.evaluation.run(node, result.model, result.ingestion)
        return True
    
    def _handle_registry(self, node: NodeConfig, result: PipelineRunResult) -> bool:
        assert isinstance(node, RegistryNodeConfig)
        result.registry = self.registry.run(node, result.model, result.evaluation)
        return True
    
def build_runner() -> PipelineRunner:
    return PipelineRunner(
        ingestion=IngestionService(),
        validation=ValidationService(),
        training=TrainingService(),
        evaluation=EvaluationService(),
        registry=RegistryService(MlflowModelRegistry(tracking_uri=MLFLOW_TRACING_URI)),
    )




app = FastAPI(title="No-Code MLOps Platform")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
runner = build_runner()

@app.post("/pipelines/run")
def run_pipeline(config: PipelineConfig) -> dict[str,Any]:
    try:
        result = runner.run(config)
    except(FileNotFoundError,ValueError,KeyError) as exc:
        raise HTTPException(status_code=400,detail=str(exc)) from exc
    
    return {
        "pipeline_id": result.pipeline_id,
        "stopped_at": result.stopped_at,
        "errors": result.errors,
        "validation_passed": result.validation.passed if result.validation else None,
        "evaluation": {
            "metric": result.evaluation.metric_name,
            "value": result.evaluation.metric_value,
            "passed": result.evaluation.passed,
        } if result.evaluation else None,
        "registry": {
            "registered": result.registry.registered,
            "model_name": result.registry.model_name,
            "version": result.registry.version,
            "skipped_reason": result.registry.skipped_reason,
        } if result.registry else None,
    }