from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class Step(BaseModel):
    action: str
    module: str
    expect_keys: Optional[List[str]] = None

class SuiteConfig(BaseModel):
    topic: Optional[str] = None
    duration: Optional[int] = None
    topics: Optional[List[str]] = None
    daily_video_target: Optional[int] = None
    allow_uploads: Optional[bool] = None

class Suite(BaseModel):
    suite: str
    description: str
    config: SuiteConfig = Field(default_factory=SuiteConfig)
    expectations: Optional[Dict[str, Any]] = None
    thresholds: Optional[Dict[str, Any]] = None
    steps: Optional[List[Step]] = None
