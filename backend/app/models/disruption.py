
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DisruptionType(str, Enum):
    SUPPLIER_DELAY = "SUPPLIER_DELAY"
    CAPACITY_DROP = "CAPACITY_DROP"
    FORCE_MAJEURE = "FORCE_MAJEURE"


class DisruptionEvent(BaseModel):
    event_id: str
    supplier_id: str
    disruption_type: DisruptionType
    delay_duration_hours: float = Field(gt=0)
    created_at: datetime
    description: str = ""
