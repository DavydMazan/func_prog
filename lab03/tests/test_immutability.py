from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from core import (
    add_service,
    add_tag,
    booking_total,
    change_status,
    extend_stay,
    update_meta,
)
from main import sample_booking
from model import Service, make_meta


def test_add_service_returns_new_booking_without_mutation() -> None:
    original = sample_booking()
    updated = add_service(original, Service("Паркінг", 400.0))
    assert updated is not original
    assert len(original.services) == 1
    assert len(updated.services) == 2


def test_booking_fields_and_nested_collections_are_immutable() -> None:
    booking = sample_booking()
    with pytest.raises(FrozenInstanceError):
        booking.status = "checked_in"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        booking.services.append(Service("Спа", 300.0))  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        booking.tags.add("vip")  # type: ignore[attr-defined]


def test_metadata_is_read_only_and_is_copied() -> None:
    source = {"source": "web"}
    proxy = make_meta(source)
    source["source"] = "changed outside"
    assert proxy["source"] == "web"
    booking = sample_booking()
    updated = update_meta(booking, campaign="winter")
    with pytest.raises(TypeError):
        booking.meta["source"] = "changed"  # type: ignore[index]
    assert updated.meta["campaign"] == "winter"
    assert booking.meta == {"source": "web", "room": "305"}


def test_pure_updates_cover_variant_operations() -> None:
    booking = sample_booking()
    tagged = add_tag(booking, "spa")
    extended = extend_stay(booking, date(2026, 11, 16))
    checked_in = change_status(booking, "checked_in")
    assert "spa" not in booking.tags and "spa" in tagged.tags
    assert booking.check_out == date(2026, 11, 14)
    assert extended.check_out == date(2026, 11, 16)
    assert booking.status == "confirmed" and checked_in.status == "checked_in"


def test_extend_stay_rejects_same_or_earlier_checkout() -> None:
    booking = sample_booking()
    with pytest.raises(ValueError):
        extend_stay(booking, booking.check_out)


def test_booking_hashability_and_total() -> None:
    booking = sample_booking()
    extended = extend_stay(booking, date(2026, 11, 15))
    assert len({booking, extended}) == 2
    assert booking_total(booking) == 3850.0
