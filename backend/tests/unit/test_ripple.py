import pytest

from backend.app.models.disruption import DisruptionType
from backend.app.models.impact import RippleImpactSummary
from backend.app.simulation.events import create_disruption_event
from backend.app.simulation.ripple import propagate_ripple_effect


def test_propagate_ripple_canonical_sup01(canonical_graph):
    """
    Verify AC-03, AC-04, and AC-05 on the canonical graph for SUP-01 (8-hour delay).
    """
    event = create_disruption_event(
        supplier_id="SUP-01",
        disruption_type=DisruptionType.SUPPLIER_DELAY,
        delay_duration_hours=8.0,
    )

    impact = propagate_ripple_effect(canonical_graph, event)

    # Model and Root Validation
    assert isinstance(impact, RippleImpactSummary)
    assert impact.disrupted_supplier == "SUP-01"

    # AC-03: Downstream dependencies identified (10 nodes reachable from SUP-01)
    assert impact.total_affected_nodes == 10

    # AC-04: Affected BOM parts identified
    assert "PART-01" in impact.affected_parts

    # AC-05: Affected finished products identified
    assert "PROD-01" in impact.affected_products

    # Downstream orders ready for Anushka's prediction module
    assert "ORD-01" in impact.affected_orders
    assert "ORD-02" in impact.affected_orders


def test_propagate_ripple_invalid_supplier(canonical_graph):
    """
    Verify that an unknown or invalid supplier raises ValueError.
    """
    class FakeEvent:
        supplier_id = "SUP-99"

    with pytest.raises(ValueError, match="Supplier SUP-99 not found in graph"):
        propagate_ripple_effect(canonical_graph, FakeEvent())

