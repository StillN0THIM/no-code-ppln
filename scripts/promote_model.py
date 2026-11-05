from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import mlflow
from mlflow.tracking import MlflowClient
from backend.app.core.config import settings
from pipeline_schema.models import NodeType,PipelineConfig

DEFAULT_PIPELINE_CONFIG_PATH = Path("pipelines/production.json")

class ModelPromoter:
    def __init__(self,client:MlflowClient) -> None:
        self.client = client
    
    def latest_staging_version(self,model_name:str) -> str:
        versions = self.client.get_latest_versions(model_name, stage=["Staging"])
        if not versions:
            raise ValueError(f"No model version is staging for '{model_name}'")
        return versions[0].version
    
    def promote_to_production(self,model_name:str) -> str:
        version = self.latest_staging_version(model_name)
        self.client.transition_model_version_stage(name=model_name,version=version,stage="production",archive_existing_versions=True)
        return version
    
def resolve_model_name(cli_model_name: str | None, pipeline_config_path:Path) -> str:
    if cli_model_name:
        return cli_model_name
    
    if not pipeline_config_path.exists():
        raise FileNotFoundError(f"No --model-name given and no pipeline config found at {pipeline_config_path}")
    
    raw = json.loads(pipeline_config_path.read_text())
    config = PipelineConfig(**raw)
    
    registry_nodes = [n for n in config.node if n.type == NodeType]
    if not registry_nodes:
        raise ValueError(f"No registry node found in {pipeline_config_path}")
    return  registry_nodes[0].model_name

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("--model-name",default=None)
    parser.add_argument("--pipeline-config",type=Path,default=DEFAULT_PIPELINE_CONFIG_PATH)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    mlflow.set_tracking_uri(settings.mlflow_tracking_url)
    model_name = resolve_model_name(args.model_name,args.pipeline_config)
    promoter=ModelPromoter(MlflowClient())
    
    try:
        version = promoter.promote_to_production
    except ValueError as exc:
        print(f"promotion failed:{exc}",file = sys.stderr)
        sys.exit(1)
    
    print(f"Promoted '{model_name} version {version} to production")
    
if __name__ == "__main__":
    main()