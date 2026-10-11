from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from sklearn.base import BaseEstimator
from sklearn.metrics import(
    accuracy_score,f1_score,mean_absolute_error,mean_squared_error,precision_score,r2_score,recall_score
)

from backend.app.services.ingestion import IngestionResult
from pipeline_schema.models import EvaluationNodeConfig

@dataclass
class EvaluationResult:
    metric_name:str
    metric_value: float
    threshold: float
    passed:bool

class MetricRegistry:
    _REGISTRY: dict[str,Callable] = {
        "accuracy": accuracy_score,
        "f1": lambda y_true, y_pred: f1_score(y_true,y_pred,average="weighted"),
        "precision":lambda y_true,y_pred:precision_score(y_true,y_pred,average="weighted"),
        "recall":lambda y_true,y_pred:recall_score(y_true,y_pred,average="weighted"),
        "r2":r2_score,
        "mse":mean_squared_error,
        "mae":mean_absolute_error,
    }
    
    _LOWER_IS_BETTER = {"mse","mae"}
    
    @classmethod   
    def score(cls, metric:str , y_true,y_pred) -> float:
        scorer = cls._REGISTRY.get(metric)
        if scorer is None:
            raise ValueError(f"unknown metric: {metric}")
        return float(scorer(y_true,y_pred))
    
    @classmethod
    def passes_threshold(cls,metric:str,value:float, threshold:float) -> bool:
        if metric in cls._LOWER_IS_BETTER:
            return value<=threshold
        return value>=threshold
    
    @classmethod
    def register(cls,name:str,scorer:callable,lower_is_better:bool = False) -> None:
        cls._REGISTRY[name] = scorer
        if lower_is_better:
            cls._LOWER_IS_BETTER.add(name)
            
class EvaluationService:
    def __init__(self,registry:type[MetricRegistry]=MetricRegistry):
        self.registry = registry
    
    def run(self,config:EvaluationNodeConfig,model:BaseEstimator,data:IngestionResult) -> EvaluationResult:
        x_test = data.test_df[data.feature_columns]
        y_test = data.test_df[data.target_columns]
        y_pred = model.predict(x_test)
        
        value = self.registry.score(config.metric, y_test,y_pred)
        passed = self.registry.passes_threshold(config.metric,value,config.threshold)
        
        return EvaluationResult(
            metric_name=config.metric,
            metric_value=value,
            threshold=config.threshold,
            passed=passed
        )