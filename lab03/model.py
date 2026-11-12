"""Immutable domain model for hotel bookings (laboratory variant 6)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date
from types import MappingProxyType
from typing import Literal

BookingStatus = Literal[
    "pending", "confirmed", "checked_in", "checked_out", "cancelled"
]


@dataclass(frozen=True, slots=True)
class Guest:
    guest_id: int
    full_name: str
    email: str


@dataclass(frozen=True, slots=True)
class Service:
    name: str
    price: float


@dataclass(frozen=True, slots=True)
class Booking:
    booking_id: int
    guest: Guest
    check_in: date
    check_out: date
    room_rate_per_night: float
    services: tuple[Service, ...] = ()
    status: BookingStatus = "pending"
    tags: frozenset[str] = frozenset()
    # MappingProxyType is read-only but unhashable; metadata participates in
    # equality while being excluded from the generated hash.
    meta: Mapping[str, str] = field(
        default_factory=lambda: MappingProxyType({}), hash=False
    )


def make_meta(
    values: Mapping[str, str] | None = None, **kwargs: str
) -> Mapping[str, str]:
    """Return a read-only proxy over a fresh copy of string metadata."""
    copied = dict(values or {})
    copied.update(kwargs)
    return MappingProxyType(copied)
