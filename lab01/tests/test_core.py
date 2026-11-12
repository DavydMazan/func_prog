"""Модульні тести для чистого ядра системи доставки (Варіант 6)."""

from __future__ import annotations

from copy import deepcopy

import pytest

from core import (
    DeliveryType,
    ParcelInput,
    calculate_base_tariff,
    calculate_surcharge,
    compose,
    filter_by_delivery_type,
    make_delivery_processor,
    make_multiplier,
    process_parcels_pure,
)


@pytest.fixture
def sample_parcels() -> list[ParcelInput]:
    """Фікстура з набором тестових посилок."""
    return [
        {
            "id": 1,
            "weight_kg": 4.0,
            "distance_km": 50.0,
            "delivery_type": "standard",
            "paid": True,
        },
        {
            "id": 2,
            "weight_kg": 15.0,
            "distance_km": 300.0,
            "delivery_type": "express",
            "paid": True,
        },
        {
            "id": 3,
            "weight_kg": 2.0,
            "distance_km": 20.0,
            "delivery_type": "courier",
            "paid": False,
        },
        {
            "id": 4,
            "weight_kg": 50.0,
            "distance_km": 100.0,
            "delivery_type": "standard",
            "paid": True,
        },
    ]


def test_referential_transparency(sample_parcels: list[ParcelInput]) -> None:
    """Однаковий вхід гарантує ідентичний вихід (референтна прозорість)."""
    multipliers: dict[DeliveryType, float] = {
        "standard": 1.0,
        "express": 1.5,
        "courier": 1.3,
    }
    r1 = process_parcels_pure(
        sample_parcels,
        max_weight_kg=30.0,
        rate_per_kg=10.0,
        rate_per_km=2.0,
        type_multipliers=multipliers,
        heavy_threshold_kg=10.0,
        heavy_fee=50.0,
        remote_threshold_km=200.0,
        remote_rate=0.1,
    )
    r2 = process_parcels_pure(
        sample_parcels,
        max_weight_kg=30.0,
        rate_per_kg=10.0,
        rate_per_km=2.0,
        type_multipliers=multipliers,
        heavy_threshold_kg=10.0,
        heavy_fee=50.0,
        remote_threshold_km=200.0,
        remote_rate=0.1,
    )
    assert r1 == r2


def test_no_input_mutation(sample_parcels: list[ParcelInput]) -> None:
    """Чисте ядро не змінює вхідний список чи словники посилок."""
    original = deepcopy(sample_parcels)
    multipliers: dict[DeliveryType, float] = {
        "standard": 1.0,
        "express": 1.5,
        "courier": 1.3,
    }
    process_parcels_pure(
        sample_parcels,
        max_weight_kg=30.0,
        rate_per_kg=10.0,
        rate_per_km=2.0,
        type_multipliers=multipliers,
        heavy_threshold_kg=10.0,
        heavy_fee=50.0,
        remote_threshold_km=200.0,
        remote_rate=0.1,
    )
    assert sample_parcels == original


def test_callable_policies_and_factory(
    sample_parcels: list[ParcelInput],
) -> None:
    """Перевірка Callable-політик тарифу, надбавки, прийнятності та часу."""
    multipliers: dict[DeliveryType, float] = {
        "standard": 1.0,
        "express": 1.5,
        "courier": 1.3,
    }

    def accept(parcel: ParcelInput) -> bool:
        return parcel["paid"] and parcel["weight_kg"] <= 30.0

    def tariff(parcel: ParcelInput) -> float:
        return calculate_base_tariff(
            parcel,
            rate_per_kg=10.0,
            rate_per_km=2.0,
            type_multipliers=multipliers,
        )

    def surcharge(base_cost: float, parcel: ParcelInput) -> float:
        return calculate_surcharge(
            base_cost,
            parcel,
            heavy_threshold_kg=10.0,
            heavy_fee=50.0,
            remote_threshold_km=200.0,
            remote_rate=0.1,
        )

    def fixed_clock() -> float:
        return 1700000000.0

    processor = make_delivery_processor(
        accept=accept,
        tariff_policy=tariff,
        surcharge_policy=surcharge,
        now_fn=fixed_clock,
    )
    report = processor(sample_parcels)

    # #1: base = (4*10 + 50*2)*1.0 = 140.0; surcharge = 0.0 -> total = 140.0
    # #2: base = (15*10 + 300*2)*1.5 = 1125.0; surcharge = 50 + 112.5 = 162.5
    # #3 не оплачена, #4 перевищує ліміт ваги 30 кг
    assert report["count"] == 2
    assert report["total_base_cost"] == 1265.0
    assert report["total_surcharge"] == 162.5
    assert report["total_revenue"] == 1427.5
    assert report["parcels"][0]["processed_at"] == 1700000000.0


def test_compose_and_multiplier() -> None:
    """Перевірка композиції функцій та фабрики множників."""
    double = make_multiplier(2.0)

    def add_ten(value: float) -> float:
        return value + 10.0

    pipeline = compose(add_ten, double)
    assert pipeline(15.0) == 40.0


def test_filter_by_delivery_type(sample_parcels: list[ParcelInput]) -> None:
    """Фільтрація повертає новий список без зміни вихідного."""
    original = deepcopy(sample_parcels)
    express_only = filter_by_delivery_type(sample_parcels, "express")
    assert len(express_only) == 1
    assert express_only[0]["id"] == 2
    assert sample_parcels == original
