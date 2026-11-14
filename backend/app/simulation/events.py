
from datetime import datetime, timezone
from uuid import uuid4

from app.models.disruption import DisruptionEvent, DisruptionType


VALID_TIER1_SUPPLIERS = {"SUP-01", "SUP-02"}


def create_disruption_event(
    supplier_id: str,
    disruption_type: DisruptionType = DisruptionType.SUPPLIER_DELAY,
    delay_duration_hours: float = 8.0,
    description: str = "",
) -> DisruptionEvent:

    if supplier_id not in VALID_TIER1_SUPPLIERS:
        raise ValueError(f"Unknown supplier ID: {supplier_id}")

    return DisruptionEvent(
        event_id=str(uuid4()),
        supplier_id=supplier_id,
        disruption_type=disruption_type,
        delay_duration_hours=delay_duration_hours,
        created_at=datetime.now(timezone.utc),
        description=description,
    )
