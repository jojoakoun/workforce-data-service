import pandas as pd

from app.loader import to_database_value


def test_to_database_value():
    """
    Check that normal values remain unchanged.
    """
    assert to_database_value(10) == 10
    assert to_database_value("Term") == "Term"


def test_to_database_value_with_missing_value():
    """
    Check that pandas missing values become None.
    """
    assert to_database_value(pd.NA) is None
    assert to_database_value(float("nan")) is None