from __future__ import annotations
from typing import Any
import mlflow.pyfunc
import pandas as pd
from fastapi import FastAPI,HTTPException
from mlflow.tracking import MlflowClient
from pydantic import BaseModel
from serving.app.config import setting 

class PredictionRequest(BaseModel):
    features: dict[str,Any]

class PredictionResponse(BaseModel):
    prediction:Any
    model_name: str
    model_version: str

class ProductionModelLoader:
    def __init__(self,tracking_uri:str)->None:
        self.tracking_uri=tracking_uri
        self.client = MlflowClient(tracking_uri=tracking_uri)
    
    def load(self,model_name:str) -> tuple[mlflow.pyfunc.PyFuncModel,str]:
        versions = self.client.get_latest_versions(model_name,stages=["Production"])
        if not versions:
            raise ValueError(f"No Production version found for '{model_name}'")
        
        version = versions[0].version
        model_uri = f"models:/{model_name}/production"
        model = mlflow.pyfunc.load_model(model_uri)
        return model,version

class PredictionService:
    def __init__(self,model:mlflow.pyfunc.PyFuncModel,model_name:str,model_version:str)->None:
        self.model = model
        self.model_name=model_name
        self.model_version = model_version
    
    def predict(self,feature:dict[str,Any])->PredictionResponse:
        df = pd.DataFrame([feature])
        prediction = self.model.predict(df)[0]
        return PredictionResponse(
            prediction=prediction,
            model_name=self.model_name,
            model_version=self.model_version,
        )

app = FastAPI(title="Model Service")
_loader = ProductionModelLoader(tracking_uri=setting.mlflow_tracking_uri)
_service: PredictionService | None = None

def get_service()->PredictionService:
    global _service
    if _service is None:
        model, version = _loader.load(setting.model_name)
        _service = PredictionService(model,setting.model_name,version)
    return _service

@app.post("/predict",response_model=PredictionResponse)
def predict(request:PredictionRequest)->PredictionResponse:
    try:
        service = get_service()
    except ValueError as exc:
        raise HTTPException(status_code=503,detail=str(exc)) from exc
    
    return service.predict(request.features)

@app.post("/reload")
def reload_model() -> dict[str, str]:
    global _service
    _service = None
    service = get_service()
    return {"status": "reloaded", "model_version": service.model_version}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}