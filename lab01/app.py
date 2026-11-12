"""Оболонка побічних ефектів (I/O) для системи доставки."""

from __future__ import annotations

import time

from core import (
    DeliveryReport,
    DeliveryType,
    ParcelInput,
    calculate_base_tariff,
    calculate_surcharge,
    compose,
    make_delivery_processor,
    make_multiplier,
)


def sample_parcels() -> list[ParcelInput]:
    """Повертає тестовий набір вхідних посилок."""
    return [
        {
            "id": 101,
            "weight_kg": 2.5,
            "distance_km": 40.0,
            "delivery_type": "standard",
            "paid": True,
        },
        {
            "id": 102,
            "weight_kg": 18.0,
            "distance_km": 350.0,
            "delivery_type": "express",
            "paid": True,
        },
        {
            "id": 103,
            "weight_kg": 5.0,
            "distance_km": 120.0,
            "delivery_type": "courier",
            "paid": False,
        },
        {
            "id": 104,
            "weight_kg": 45.0,
            "distance_km": 200.0,
            "delivery_type": "standard",
            "paid": True,
        },
        {
            "id": 105,
            "weight_kg": 1.2,
            "distance_km": 15.0,
            "delivery_type": "courier",
            "paid": True,
        },
    ]


def render_report(report: DeliveryReport) -> None:
    """Виводить сформований звіт у консоль (ізольований I/O)."""
    print("=== Звіт системи доставки ===")
    print(f"Оброблено посилок: {report['count']}")
    for p in report["parcels"]:
        print(
            f"  Посилка #{p['id']} [{p['delivery_type']}]: "
            f"вага={p['weight_kg']} кг, відстань={p['distance_km']} км | "
            f"база={p['base_cost']:.2f} грн, "
            f"надбавка={p['surcharge']:.2f} грн, "
            f"разом={p['total_cost']:.2f} грн (ts={p['processed_at']})"
        )
    print(f"Сумарний базовий тариф: {report['total_base_cost']:.2f} грн")
    print(f"Сумарні надбавки:      {report['total_surcharge']:.2f} грн")
    print(f"Загальна виручка:      {report['total_revenue']:.2f} грн")


def run() -> None:
    """Точка входу: налаштовує політики, запускає ядро та друкує звіт."""
    multipliers: dict[DeliveryType, float] = {
        "standard": 1.0,
        "express": 1.5,
        "courier": 1.3,
    }

    def accept_policy(parcel: ParcelInput) -> bool:
        return (
            parcel["paid"]
            and 0 < parcel["weight_kg"] <= 30.0
            and parcel["distance_km"] > 0
        )

    def tariff_policy(parcel: ParcelInput) -> float:
        return calculate_base_tariff(
            parcel,
            rate_per_kg=12.0,
            rate_per_km=1.5,
            type_multipliers=multipliers,
        )

    fuel_adjust = make_multiplier(1.05)

    def add_packaging_fee(surcharge: float) -> float:
        return surcharge + 15.0 if surcharge > 0 else 0.0

    adjusted_surcharge = compose(add_packaging_fee, fuel_adjust)

    def surcharge_policy(base_cost: float, parcel: ParcelInput) -> float:
        raw_surcharge = calculate_surcharge(
            base_cost,
            parcel,
            heavy_threshold_kg=10.0,
            heavy_fee=80.0,
            remote_threshold_km=250.0,
            remote_rate=0.15,
        )
        return adjusted_surcharge(raw_surcharge)

    processor = make_delivery_processor(
        accept=accept_policy,
        tariff_policy=tariff_policy,
        surcharge_policy=surcharge_policy,
        now_fn=time.time,
    )

    parcels = sample_parcels()
    report = processor(parcels)
    render_report(report)


if __name__ == "__main__":
    run()
