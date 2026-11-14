
import pytest
from pydantic import ValidationError

from app.models.disruption import DisruptionType
from app.simulation.events import create_disruption_event


def test_create_valid_disruption_event():
    event = create_disruption_event(
        supplier_id="SUP-01",
        delay_duration_hours=8.0,
    )

    assert event.supplier_id == "SUP-01"
    assert event.disruption_type == DisruptionType.SUPPLIER_DELAY
    assert event.delay_duration_hours == 8.0
    assert event.event_id
    assert event.created_at is not None


def test_invalid_supplier_raises_value_error():
    with pytest.raises(ValueError):
        create_disruption_event(supplier_id="SUP-99")


def test_zero_delay_raises_validation_error():
    with pytest.raises(ValidationError):
        create_disruption_event(
            supplier_id="SUP-01",
            delay_duration_hours=0,
        )


def test_negative_delay_raises_validation_error():
    with pytest.raises(ValidationError):
        create_disruption_event(
            supplier_id="SUP-01",
            delay_duration_hours=-5,
        )
