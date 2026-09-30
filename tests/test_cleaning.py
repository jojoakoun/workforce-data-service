import pandas as pd

from app.cleaning import (
    clean_reference_department_names,
    clean_tenure_values,
    clean_text,
    clean_workforce_department_names,
    correct_known_department_names,
    clean_headcount_values,
    clean_reference_duplicates,
)


def test_clean_text():
    """
    Check that extra whitespace is removed from text values.
    """
    assert clean_text(" Term ") == "Term"
    assert clean_text("Public  Service") == "Public Service"


def test_clean_text_with_missing_value():
    """
    Check that a missing value remains missing.
    """
    result = clean_text(pd.NA)

    assert pd.isna(result)


def test_clean_tenure_values():
    """
    Check that tenure values are cleaned in all workforce sheets.
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

    workbook = clean_tenure_values(workbook)

    values = workbook[
        "Federal Public Service"
    ]["tenure"].tolist()

    assert values == [
        "Term",
        "Indeterminate",
    ]


def test_clean_workforce_department_names():
    """
    Check that department names are cleaned in all workforce sheets.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "department": [" Department  A "]
        }),
        "RCMP": pd.DataFrame({
            "department": [" RCMP "]
        }),
        "CAF": pd.DataFrame({
            "department": ["Canadian  Armed Forces"]
        }),
    }

    workbook = clean_workforce_department_names(workbook)

    assert (
        workbook["Federal Public Service"]["department"][0]
        == "Department A"
    )
    assert workbook["RCMP"]["department"][0] == "RCMP"
    assert (
        workbook["CAF"]["department"][0]
        == "Canadian Armed Forces"
    )


def test_clean_reference_department_names():
    """
    Check that all department reference text values are cleaned.
    """
    workbook = {
        "Departments": pd.DataFrame({
            "long_name_en": [" Canadian Armed Forces "],
            "long_name_fr": [" Forces armées canadiennes "],
            "short_name_en": [" CAF "],
            "short_name_fr": [" FAC "],
        })
    }

    workbook = clean_reference_department_names(workbook)

    department = workbook["Departments"].iloc[0]

    assert department["long_name_en"] == "Canadian Armed Forces"
    assert department["long_name_fr"] == "Forces armées canadiennes"
    assert department["short_name_en"] == "CAF"
    assert department["short_name_fr"] == "FAC"

def test_correct_known_department_names():
    """
    Check that known department name errors are corrected.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "department": ["Privy Council Officee"]
        }),
        "RCMP": pd.DataFrame({
            "department": ["RCMP"]
        }),
        "CAF": pd.DataFrame({
            "department": ["CAF"]
        }),
    }

    workbook = correct_known_department_names(workbook)

    result = workbook[
        "Federal Public Service"
    ]["department"][0]

    assert result == "Privy Council Office"
    
def test_clean_headcount_values():
    """
    Check that negative headcount becomes missing.

    Keep valid and existing missing values unchanged.
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

    workbook = clean_headcount_values(workbook)

    headcount = workbook[
        "Federal Public Service"
    ]["headcount"]

    assert headcount[0] == 100
    assert pd.isna(headcount[1])
    assert pd.isna(headcount[2])
    
def test_clean_reference_duplicates():
    """
    Check that exact reference duplicates are removed.
    """
    workbook = {
        "Departments": pd.DataFrame({
            "long_name_en": ["Department A", "Department A"],
            "long_name_fr": ["Ministère A", "Ministère A"],
        })
    }

    workbook = clean_reference_duplicates(workbook)

    assert len(workbook["Departments"]) == 1