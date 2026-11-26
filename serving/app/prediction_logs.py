from __future__ import annotations
import json
from dataclasses import dataclass
from datetime import datetime,timezone
from typing import Any
from sqlalchemy import Column,DateTime,Integer,MetaData,String,Table
from sqlalchemy.engine import Engine

metadata = MetaData()

prediction_logs = Table(
    "prediction_logs",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("model_name", String, nullable=False),
    Column("model_version", String, nullable=False),
    Column("features_json", String, nullable=False),
    Column("prediction", String, nullable=False),
    Column("logged_at", DateTime, nullable=False),
)

@dataclass
class LoggedPrediction:
    model_name: str
    model_version: str
    features: dict[str,Any]
    prediction: Any

class PredictionLogger:
    def __init__(self,engine:Engine) -> None:
        self.engine = engine
        metadata.create_all(self.engine, table=[prediction_logs])

    def log(self,entry:LoggedPrediction)->None:
        with self.engine.begin() as conn:
            conn.execute(
                prediction_logs.insert().value(
                    model_name = entry.model_name,
                    model_version = entry.model_version,
                    features_json = json.dumps(entry.features),
                    prediction = str(entry.prediction),
                    logged_at = datetime.now(timezone.utc),
                )
            )