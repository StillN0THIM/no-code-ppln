from __future__ import annotations
from dataclasses import dataclass
import mlflow
import mlflow.sklearn
from sklearn.base import BaseEstimator
from backend.app.services.evaluation import EvaluationResult
from pipeline_schema.models import RegistryNodeConfig

@dataclass
class RegistryResult:
    registered: bool
    model_name = str | None = None
    version = str | None = None
    run_id = str | None = None
    skipped_reason = str | None = None

class MlflowModelRegistry:
    def __init__(self , tracking_uri:str)->None:
        self.tracking_uri = tracking_uri
    
    def log_and_register(
        self,
        model: BaseEstimator,
        model_name:str,
        stage:str,
        metric_name:str,
        metric_value:float,
    ) -> RegistryResult:
        mlflow.set_tracking_uri(self.tracking_uri)
        
        with mlflow.start_run() as run:
            mlflow.log_metric(metric_name,metric_value)
            model_info = mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path="model",
                registered_model_name=model_name,
            )
            
            client = mlflow.tracking.MlflowClient()
            version = client.get_latest_versions(model_name,stages=["None"])[0].version
            client.transition_model_version_stage(
                name=model_name,
                version=version,
                stage=stage
            )
            
            return RegistryResult(
                registered=True,
                model_name=model_name,
                version=version,
                run_id=run.info.run_id
            )

class RegistryService:
    def __init__(self,registry:MlflowModelRegistry) -> None:
        self.registry = registry
    
    def run(self,config:RegistryNodeConfig,model:BaseEstimator,evaluation:EvaluationResult,) -> RegistryResult:
        if not evaluation.passed:
            return RegistryResult(
                registered=False,
                skipped_reason=(f"Evaluation gate failed: {evaluation.metric_name}={evaluation.metric_value} did not cleat threshold {evaluation.threshold}")
            )
            
        return self.registry.log_and_register(
            model=model,
            model_name=config.model_name,
            stage=config.metric_name,
            metric_value=evaluation.metric_value
        )