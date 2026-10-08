from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from pipeline_schema.models import DatasetNodeConfig

@dataclass
class IngestionResult:
    tain_df: pd.DataFrame
    test_df:pd.DataFrame
    target_columns:list[str]

class DatasetLoader:
    _LOADERS = {
        ".csv":pd.read_csv,
        ".parquet":pd.read_parquet,
        ".json":pd.read_json,
    }
    
    def load(self,source_path:str) -> pd.DataFrame:
        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found at {source_path}")

        loader = self._LOADERS.get(path.suffix.lower())
        if loader is None:
            raise ValueError(f"unsupported dataset format:{path.suffix}")
        
        return loader(path)


class IngestionService:
    def __init__(self , loader:DatasetNodeConfig | None = None) -> None:
        self.loader = loader or DatasetLoader()
    
    def run(self, config:DatasetNodeConfig) -> IngestionResult:
        df = self.loader.load(config.source_path)
        
        if config.target_column not in df.columns:
            raise ValueError(f"target column '{config.target_column} not found in the dataset")
        
        feature_column = [c for c in df.columns if c != config.target_column]
        
        train_df , test_df = train_test_split(
            df,test_size=config.test_size,random_state=42
        )
        
        return IngestionResult(
            train_df = train_df.reset_index(drop=True),
            test_df=test_df.reset_index(drop=True),
            target_columns=config.target_column,
            feature_column=feature_column,
        )