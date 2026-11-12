from itertools import accumulate
from operator import mul

from core import first_balances, positive_transactions, running_balance
from streams import take


def test_positive_transactions_and_running_balance() -> None:
    values = [-10.0, 12.0, 3.0, 0.0, -2.0, 5.0]
    assert take(10, positive_transactions(values)) == [12.0, 3.0, 5.0]
    assert list(running_balance(values)) == [12.0, 15.0, 20.0]
    assert first_balances(values, 2) == [12.0, 15.0]


def test_itertools_accumulate_sum_and_product() -> None:
    assert list(accumulate([1, 2, 3, 4])) == [1, 3, 6, 10]
    assert list(accumulate([1, 2, 3, 4], mul)) == [1, 2, 6, 24]
