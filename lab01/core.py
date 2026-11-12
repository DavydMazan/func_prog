"""Чисте розрахункове ядро системи доставки (Варіант 6)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Literal, TypedDict, TypeVar

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")

DeliveryType = Literal["standard", "express", "courier"]


class ParcelInput(TypedDict):
    """Вхідна структура даних посилки (не мутується)."""

    id: int
    weight_kg: float
    distance_km: float
    delivery_type: DeliveryType
    paid: bool


class ProcessedParcel(ParcelInput):
    """Новий запис обробленої посилки з розрахованими полями."""

    base_cost: float
    surcharge: float
    total_cost: float
    processed_at: float | None


class DeliveryReport(TypedDict):
    """Підсумковий звіт обробки партії посилок."""

    count: int
    total_base_cost: float
    total_surcharge: float
    total_revenue: float
    parcels: list[ProcessedParcel]


AcceptFn = Callable[[ParcelInput], bool]
TariffFn = Callable[[ParcelInput], float]
SurchargeFn = Callable[[float, ParcelInput], float]
NowFn = Callable[[], float]


def compose(f: Callable[[B], C], g: Callable[[A], B]) -> Callable[[A], C]:
    """Композиція двох функцій: (f o g)(x) = f(g(x))."""
    return lambda x: f(g(x))


def make_multiplier(factor: float) -> Callable[[float], float]:
    """Фабрика функцій-множників для масштабування вартості."""
    return lambda value: value * factor


def calculate_base_tariff(
    parcel: ParcelInput,
    *,
    rate_per_kg: float,
    rate_per_km: float,
    type_multipliers: Mapping[DeliveryType, float],
) -> float:
    """Обчислює базову вартість доставки без використання глобального стану."""
    raw_cost = (
        parcel["weight_kg"] * rate_per_kg
        + parcel["distance_km"] * rate_per_km
    )
    multiplier = type_multipliers[parcel["delivery_type"]]
    return round(raw_cost * multiplier, 2)


def calculate_surcharge(
    base_cost: float,
    parcel: ParcelInput,
    *,
    heavy_threshold_kg: float,
    heavy_fee: float,
    remote_threshold_km: float,
    remote_rate: float,
) -> float:
    """Обчислює суму надбавок за велику вагу та дальню відстань."""
    weight_extra = (
        heavy_fee if parcel["weight_kg"] > heavy_threshold_kg else 0.0
    )
    distance_extra = (
        base_cost * remote_rate
        if parcel["distance_km"] > remote_threshold_km
        else 0.0
    )
    return round(weight_extra + distance_extra, 2)


def with_delivery_totals(
    parcel: ParcelInput,
    *,
    base_cost: float,
    surcharge: float,
    total_cost: float,
    processed_at: float | None = None,
) -> ProcessedParcel:
    """Повертає новий словник посилки з результатами без мутації оригіналу."""
    return {
        "id": parcel["id"],
        "weight_kg": parcel["weight_kg"],
        "distance_km": parcel["distance_km"],
        "delivery_type": parcel["delivery_type"],
        "paid": parcel["paid"],
        "base_cost": base_cost,
        "surcharge": surcharge,
        "total_cost": total_cost,
        "processed_at": processed_at,
    }


def filter_by_delivery_type(
    parcels: Iterable[ParcelInput],
    delivery_type: DeliveryType,
) -> list[ParcelInput]:
    """Повертає новий список посилок заданого типу без побічних ефектів."""
    return [p for p in parcels if p["delivery_type"] == delivery_type]


def process_parcels_pure(
    parcels: Iterable[ParcelInput],
    *,
    max_weight_kg: float,
    rate_per_kg: float,
    rate_per_km: float,
    type_multipliers: Mapping[DeliveryType, float],
    heavy_threshold_kg: float,
    heavy_fee: float,
    remote_threshold_km: float,
    remote_rate: float,
) -> DeliveryReport:
    """Чиста функція базової обробки посилок з явно переданими параметрами."""
    processed: list[ProcessedParcel] = []
    total_base = 0.0
    total_surcharge = 0.0
    total_revenue = 0.0

    for parcel in parcels:
        if not parcel["paid"] or not (0 < parcel["weight_kg"] <= max_weight_kg):
            continue
        base_cost = calculate_base_tariff(
            parcel,
            rate_per_kg=rate_per_kg,
            rate_per_km=rate_per_km,
            type_multipliers=type_multipliers,
        )
        surcharge = calculate_surcharge(
            base_cost,
            parcel,
            heavy_threshold_kg=heavy_threshold_kg,
            heavy_fee=heavy_fee,
            remote_threshold_km=remote_threshold_km,
            remote_rate=remote_rate,
        )
        total_cost = round(base_cost + surcharge, 2)
        processed.append(
            with_delivery_totals(
                parcel,
                base_cost=base_cost,
                surcharge=surcharge,
                total_cost=total_cost,
            )
        )
        total_base = round(total_base + base_cost, 2)
        total_surcharge = round(total_surcharge + surcharge, 2)
        total_revenue = round(total_revenue + total_cost, 2)

    return {
        "count": len(processed),
        "total_base_cost": total_base,
        "total_surcharge": total_surcharge,
        "total_revenue": total_revenue,
        "parcels": processed,
    }


def make_delivery_processor(
    *,
    accept: AcceptFn,
    tariff_policy: TariffFn,
    surcharge_policy: SurchargeFn,
    now_fn: NowFn | None = None,
) -> Callable[[Iterable[ParcelInput]], DeliveryReport]:
    """Фабрика вищого порядку, що конфігурує чистий обробник доставки."""

    def process(parcels: Iterable[ParcelInput]) -> DeliveryReport:
        processed: list[ProcessedParcel] = []
        total_base = 0.0
        total_surcharge = 0.0
        total_revenue = 0.0

        for parcel in parcels:
            if not accept(parcel):
                continue
            base_cost = round(tariff_policy(parcel), 2)
            surcharge = round(surcharge_policy(base_cost, parcel), 2)
            total_cost = round(base_cost + surcharge, 2)
            timestamp = now_fn() if now_fn is not None else None

            processed.append(
                with_delivery_totals(
                    parcel,
                    base_cost=base_cost,
                    surcharge=surcharge,
                    total_cost=total_cost,
                    processed_at=timestamp,
                )
            )
            total_base = round(total_base + base_cost, 2)
            total_surcharge = round(total_surcharge + surcharge, 2)
            total_revenue = round(total_revenue + total_cost, 2)

        return {
            "count": len(processed),
            "total_base_cost": total_base,
            "total_surcharge": total_surcharge,
            "total_revenue": total_revenue,
            "parcels": processed,
        }

    return process
