"""Small mutable baseline used only for a before/after timing comparison."""

from __future__ import annotations

from datetime import date
from typing import TypedDict


class MutableBooking(TypedDict):
    check_in: date
    check_out: date
    room_rate: float
    services: list[float]
    tags: set[str]
    status: str


def mutable_booking() -> MutableBooking:
    return {
        "check_in": date(2026, 11, 12),
        "check_out": date(2026, 11, 14),
        "room_rate": 1800.0,
        "services": [250.0, 400.0],
        "tags": {"weekend"},
        "status": "confirmed",
    }


def mutate_booking(booking: MutableBooking) -> float:
    services = booking["services"]
    tags = booking["tags"]
    services.append(125.0)
    tags.add("spa")
    booking["status"] = "checked_in"
    nights = (booking["check_out"] - booking["check_in"]).days
    return round(nights * booking["room_rate"] + sum(services), 2)
