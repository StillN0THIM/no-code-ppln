from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from sklearn.base import BaseEstimator
from sklearn.ensemble import RandomForestClassifier,RandomForestRegressor
from sklearn.linear_model import LogisticRegression,LinearRegression
from backend.app.services.ingestion import IngestionResult
from pipeline_schema.models import TrainingNodeConfig

@dataclass
class TrainingResult:
    model: BaseEstimator
    feature_columns: list[str]
    target_column: str

class ModelFactory:
    _REGISTRY: dict[str,type[BaseEstimator]] = {
        "random_forest_classifier":RandomForestClassifier,
        "random_forest_regressor":RandomForestRegressor,
        "logistic_regression":LogisticRegression,
        "linear_regression":LinearRegression,
    }
    
    @classmethod
    def create(cls, algorithm: str,hyperparameters: dict[str,Any]) -> BaseEstimator:
        model_cls=cls._REGISTRY.get(algorithm)
        if model_cls is None:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        return model_cls(**hyperparameters)
    
    @classmethod
    def register(cls,name:str,model_cls:type[BaseEstimator])->None:
        cls._REGISTRY[name] = model_cls

class TrainingService:
    def __init__(self,factory:ModelFactory | None = None) -> None:
        self.factory = factory or ModelFactory()
    
    def run(self,config:TrainingNodeConfig, data:IngestionResult) -> TrainingResult:
        model = self.factory.create(config.algorithm,config.hyperparameters)
        
        x_train = data.train_df[data.feature_columns]
        y_train = data.train_df[data.target_columns]
        model.fit(x_train,y_train)
        
        return TrainingResult(
            model=model,
            feature_columns=data.feature_columns,
            target_column=data.target_columns
        )