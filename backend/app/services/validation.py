from __future__ import annotations
from backend.app.services.ingestion import IngestionResult
from pipeline_schema.models import ValidationNodeConfig
from pipeline_schema.validators import PipelineValidator,ValidationReport

class ValidationService:
    def run(self, config:ValidationNodeConfig, data: IngestionResult) -> ValidationReport:
        validator = PipelineValidator(config)
        return validator.validate(data.train_df)