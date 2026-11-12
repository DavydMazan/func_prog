"""Pure business operations for immutable hotel booking records."""

from __future__ import annotations

from dataclasses import replace
from datetime import date

from model import Booking, BookingStatus, Service, make_meta


def add_service(booking: Booking, service: Service) -> Booking:
    """Return a booking with one appended service."""
    return replace(booking, services=booking.services + (service,))


def change_status(booking: Booking, status: BookingStatus) -> Booking:
    """Return a booking with a new lifecycle status."""
    return replace(booking, status=status)


def extend_stay(booking: Booking, new_check_out: date) -> Booking:
    """Return a booking with a later checkout date; reject non-extensions."""
    if new_check_out <= booking.check_out:
        raise ValueError("new checkout date must be later than the current date")
    return replace(booking, check_out=new_check_out)


def add_tag(booking: Booking, tag: str) -> Booking:
    """Return a booking with an additional immutable tag."""
    return replace(booking, tags=booking.tags | frozenset({tag}))


def update_meta(booking: Booking, **changes: str) -> Booking:
    """Return a booking with copied, read-only metadata."""
    updated = dict(booking.meta)
    updated.update(changes)
    return replace(booking, meta=make_meta(updated))


def booking_total(booking: Booking) -> float:
    """Calculate room charges and selected services without changing input."""
    nights = (booking.check_out - booking.check_in).days
    services_total = sum(service.price for service in booking.services)
    return round(nights * booking.room_rate_per_night + services_total, 2)
