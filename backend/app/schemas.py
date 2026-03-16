from pydantic import BaseModel
from typing import List, Dict

class PipelineStep(BaseModel):
    effect: str
    params: Dict

class PipelineRequest(BaseModel):
    pipeline: List[PipelineStep]