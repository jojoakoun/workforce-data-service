import pandas as pd
import pytest

from app.processing import (
    process_dates,
    process_departments,
    process_duplicates,
    process_fte,
    process_headcount,
    process_reference_quality,
    process_tenure,
)


def test_process_tenure():
    """
    Check that tenure values are cleaned and validated.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "tenure": ["Term ", "Indeterminate "]
        }),
        "RCMP": pd.DataFrame({
            "tenure": ["Combined"]
        }),
        "CAF": pd.DataFrame({
            "tenure": ["Combined"]
        }),
    }

    result = process_tenure(workbook)

    values = result[
        "Federal Public Service"
    ]["tenure"].tolist()

    assert values == [
        "Term",
        "Indeterminate",
    ]


def test_process_departments():
    """
    Check that department names are cleaned and validated.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "department": [" Department A "]
        }),
        "RCMP": pd.DataFrame({
            "department": [
                "Royal Canadian Mounted Police - Members"
            ]
        }),
        "CAF": pd.DataFrame({
            "department": ["Canadian Armed Forces"]
        }),
        "Departments": pd.DataFrame({
            "long_name_en": [
                "Department A",
                "Canadian Armed Forces ",
                "Royal Canadian Mounted Police - Members",
            ],
            "long_name_fr": [
                "Department A FR",
                "Forces armées canadiennes ",
                "Gendarmerie royale du Canada - Membres",
            ],
            "short_name_en": [
                "DA",
                "CAF",
                pd.NA,
            ],
            "short_name_fr": [
                "DAFR",
                "FAC",
                pd.NA,
            ],
        }),
    }

    result = process_departments(workbook)

    assert (
        result["Federal Public Service"]["department"][0]
        == "Department A"
    )

    assert (
        result["Departments"]["long_name_en"][1]
        == "Canadian Armed Forces"
    )

    assert (
        result["Departments"]["long_name_fr"][1]
        == "Forces armées canadiennes"
    )


def test_process_headcount(capsys):
    """
    Check that negative headcount becomes missing.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "headcount": [100, -20, pd.NA]
        }),
        "RCMP": pd.DataFrame({
            "headcount": [200]
        }),
        "CAF": pd.DataFrame({
            "headcount": [300]
        }),
    }

    result = process_headcount(workbook)

    output = capsys.readouterr().out

    assert "=== HEADCOUNT PROCESSING ===" in output

    headcount = result[
        "Federal Public Service"
    ]["headcount"]

    assert headcount[0] == 100
    assert pd.isna(headcount[1])
    assert pd.isna(headcount[2])


def test_process_headcount_rejects_fractional_value():
    """
    Check that fractional headcount values fail validation.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "headcount": [100, 25.5]
        }),
        "RCMP": pd.DataFrame({
            "headcount": [200]
        }),
        "CAF": pd.DataFrame({
            "headcount": [300]
        }),
    }

    with pytest.raises(ValueError):
        process_headcount(workbook)


def test_process_fte():
    """
    Check that valid FTE processing completes.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "fte": [10.5, pd.NA]
        })
    }

    result = process_fte(workbook)

    assert result is workbook


def test_process_dates():
    """
    Check that valid workforce dates complete processing.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "date": [201503]
        }),
        "RCMP": pd.DataFrame({
            "date": [201504]
        }),
        "CAF": pd.DataFrame({
            "date": [201504]
        }),
    }

    result = process_dates(workbook)

    assert result is workbook


def test_process_reference_quality():
    """
    Check that exact reference duplicates are removed.
    """
    row = {
        "long_name_en": "Department A",
        "long_name_fr": "Ministère A",
        "short_name_en": "DA",
        "short_name_fr": "MA",
    }

    workbook = {
        "Departments": pd.DataFrame([
            row,
            row,
        ])
    }

    result = process_reference_quality(workbook)

    assert len(result["Departments"]) == 1


def test_process_duplicates():
    """
    Check that unique workforce records pass validation.
    """
    row = {
        "date": 201503,
        "department": "Department A",
        "tenure": "Term",
    }

    workbook = {
        "Federal Public Service": pd.DataFrame([row]),
        "RCMP": pd.DataFrame([row]),
        "CAF": pd.DataFrame([row]),
    }

    result = process_duplicates(workbook)

    assert result is workbook