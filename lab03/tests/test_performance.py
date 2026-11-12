from baseline import mutable_booking, mutate_booking
from core import add_service, booking_total
from main import sample_booking
from model import Service


def test_mutable_and_immutable_operations_return_valid_totals() -> None:
    mutable = mutable_booking()
    mutable_total = mutate_booking(mutable)
    immutable = add_service(sample_booking(), Service("Тестова послуга", 125.0))
    immutable_total = booking_total(immutable)
    assert mutable_total > 0
    assert immutable_total > 0
