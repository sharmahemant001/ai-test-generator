from pydantic import BaseModel
from typing import List, Optional

class GenerateRequest(BaseModel):
    requirements: str

class TestCase(BaseModel):
    id: str
    type: str
    title: str
    description: str
    input: str
    expectedResult: str
    automationTemplate: Optional[str] = None

class GenerateResponse(BaseModel):
    summary: str
    coverage: int
    testCases: List[TestCase]
