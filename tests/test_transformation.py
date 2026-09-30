from datetime import date

import pandas as pd

from app.transformation import (
    convert_period,
    prepare_workforce_records,
)


def test_convert_period():
    """
    Check that YYYYMM becomes the first day of the month.
    """
    result = convert_period(201503)

    assert result == date(2015, 3, 1)


def test_prepare_workforce_records():
    """
    Check that workforce sheets are combined consistently.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "date": [201503],
            "tenure": ["Term"],
            "department": ["Department A"],
            "headcount": [10],
            "fte": [9.5],
        }),
        "RCMP": pd.DataFrame({
            "date": [201504],
            "tenure": ["Combined"],
            "department": ["RCMP"],
            "headcount": [20],
        }),
        "CAF": pd.DataFrame({
            "date": [201504],
            "tenure": ["Combined"],
            "department": ["CAF"],
            "headcount": [30],
        }),
    }

    result = prepare_workforce_records(workbook)

    assert len(result) == 3
    assert list(result.columns) == [
        "period",
        "source",
        "department",
        "tenure",
        "headcount",
        "fte",
    ]

    assert result.iloc[0]["period"] == date(2015, 3, 1)
    assert result.iloc[0]["source"] == "Federal Public Service"

    assert result.iloc[1]["source"] == "RCMP"
    assert pd.isna(result.iloc[1]["fte"])

    assert result.iloc[2]["source"] == "CAF"
    assert pd.isna(result.iloc[2]["fte"])