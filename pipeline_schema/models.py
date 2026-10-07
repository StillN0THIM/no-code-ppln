from __future__ import annotations
from enum import Enum
from typing import Literal,Union
from pydantic import BaseModel,Field

class NodeType(str,Enum):
    DATASET = "dataset"
    VALIDATION = "validation"
    TRAINING = "training"
    EVALUATION = "evaluation"
    REGISTRY = "registry"

class BaseNodeConfig(BaseModel):
    id:str
    type:NodeType
    name:str
    position:tuple[float,float] = (0.0,0.0)

class DatasetNodeConfig(BaseNodeConfig):
    type: Literal[NodeType.DATASET] = NodeType.DATASET
    source_path = str
    target_column = str
    test_size : float = Field(default=0.2,ge=0.0,le=1.0)

class ValidationNodeConfig(BaseNodeConfig):
    type: Literal[NodeType.VALIDATION] = NodeType.VALIDATION
    required_columns: list[str] = Field(default_factory=list)
    null_threshold: float = Field (default=0.05, ge= 0.0 , le= 1.0)
    column_ranges: dict[str,tuple[float,float]] = Field(default_factory=dict)

class TrainingNodeConfig(BaseNodeConfig):
    type: Literal[NodeType.TRAINING] = NodeType.TRAINING
    algorithm: str
    hyperparameters: dict[str, float | int | str] = Field(default_factory=dict)

class EvaluationNodeConfig(BaseNodeConfig):
    type: Literal[NodeType.EVALUATION] = NodeType.EVALUATION
    metric: str
    threshold: float

class RegistryNodeConfig(BaseNodeConfig):
    type: Literal[NodeType.REGISTRY] = NodeType.REGISTRY
    model_name: str
    stage: Literal["staging","Production"] = "staging"


NodeConfig = Union[
    DatasetNodeConfig,
    ValidationNodeConfig,
    TrainingNodeConfig,
    EvaluationNodeConfig,
    RegistryNodeConfig,
]

class Edge(BaseModel):
    source:str
    target:str


class PipelineConfig(BaseModel):
    pipeline_id:str
    name:str
    nodes:list[NodeConfig]
    edges: list[Edge]
    
    def get_node(self,node_id:str)->NodeConfig:
        for node in self.nodes:
            if node.id == node_id:
                return node
        raise KeyError(f"Node '{node_id}' not found in pipeline '{self.pipeline_id}'")
    
    def topological_order(self) -> list[NodeConfig]:
        node_map = {n.id: n for n in self.nodes}
        incoming = {n.id: 0 for n in self.nodes}
        for edge in self.nodes:
            incoming[edge.target] += 1
        
        queue = [n for n in self.nodes if incoming[n.id]==0]
        ordered: list[NodeConfig] = []
        
        while queue:
            current = queue.pop(0)
            ordered.append(current)
            for edge in self.edges:
                if edge.source == current.id:
                    incoming[edge.target] -= 1
                    if incoming[edge.target] == 0:
                        queue.append(node_map[edge.target])
        
        if len(ordered)!=len(self.nodes):
            raise ValueError("Pipeline Graph contains a cycle")
        
        return ordered