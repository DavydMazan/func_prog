"""Run a short hotel-booking example for laboratory work 3, variant 6."""

from datetime import date

from core import add_service, booking_total, change_status, extend_stay
from model import Booking, Guest, Service, make_meta


def sample_booking() -> Booking:
    guest = Guest(guest_id=101, full_name="Олена Коваль", email="olena@example.com")
    return Booking(
        booking_id=6001,
        guest=guest,
        check_in=date(2026, 11, 12),
        check_out=date(2026, 11, 14),
        room_rate_per_night=1800.0,
        services=(Service("Сніданок", 250.0),),
        status="confirmed",
        tags=frozenset({"weekend", "city"}),
        meta=make_meta(source="web", room="305"),
    )


def main() -> None:
    original = sample_booking()
    updated = add_service(original, Service("Паркінг", 400.0))
    updated = extend_stay(updated, date(2026, 11, 15))
    updated = change_status(updated, "checked_in")

    print("=== Система бронювання готелю ===")
    print(f"Бронювання: #{updated.booking_id}; гість: {updated.guest.full_name}")
    print(
        f"Статус: {updated.status}; "
        f"ночей: {(updated.check_out - updated.check_in).days}"
    )
    print(f"Послуг: {len(updated.services)}; сума: {booking_total(updated):.2f} грн")
    print(f"Початкове бронювання не змінено: {len(original.services)} послуга")


if __name__ == "__main__":
    main()
