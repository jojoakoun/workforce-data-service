import pandas as pd

from app.validation import (
  validate_columns, 
  validate_sheets,
  validate_workbook_structure,
  validate_tenure_values,
  validate_department_names,
  validate_headcount_values,
  validate_fte_values,
  validate_date_values,
  validate_reference_data,
  validate_workforce_duplicates
)


def test_validate_sheets():
    """
    Check that all required sheets are accepted.
    """
    workbook = {
        "Federal Public Service": None,
        "RCMP": None,
        "CAF": None,
        "Departments": None,
    }

    missing_sheets = validate_sheets(workbook)

    assert missing_sheets == []


def test_validate_columns():
    """
    Check that the required CAF columns are accepted.
    """
    workbook = {
        "CAF": pd.DataFrame(
            columns=[
                "date",
                "tenure",
                "department",
                "headcount",
            ]
        )
    }

    missing_columns = validate_columns({
        "Federal Public Service": pd.DataFrame(
            columns=[
                "date",
                "tenure",
                "department",
                "headcount",
                "fte",
            ]
        ),
        "RCMP": pd.DataFrame(
            columns=[
                "date",
                "tenure",
                "department",
                "headcount",
            ]
        ),
        "CAF": workbook["CAF"],
        "Departments": pd.DataFrame(
            columns=[
                "long_name_en",
                "long_name_fr",
                "short_name_en",
                "short_name_fr",
            ]
        ),
    })

    assert missing_columns == {}
    
    
def test_validate_workbook_structure():
    """
    Check that a workbook with the required sheets and columns is valid.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame(
            columns=["date", "tenure", "department", "headcount", "fte"]
        ),
        "RCMP": pd.DataFrame(
            columns=["date", "tenure", "department", "headcount"]
        ),
        "CAF": pd.DataFrame(
            columns=["date", "tenure", "department", "headcount"]
        ),
        "Departments": pd.DataFrame(
            columns=[
                "long_name_en",
                "long_name_fr",
                "short_name_en",
                "short_name_fr",
            ]
        ),
    }

    result = validate_workbook_structure(workbook)

    assert result is True
    
    
def test_validate_tenure_values():
    """
    Check that valid tenure values are accepted.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "tenure": ["Term", "Student", "Missing", pd.NA]
        }),
        "RCMP": pd.DataFrame({
            "tenure": ["Combined"]
        }),
        "CAF": pd.DataFrame({
            "tenure": ["Combined"]
        }),
    }

    result = validate_tenure_values(workbook)

    assert result == {}
    
def test_validate_invalid_tenure_value():
    """
    Check that an unexpected tenure value is reported.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "tenure": ["Permanent"]
        }),
        "RCMP": pd.DataFrame({
            "tenure": ["Combined"]
        }),
        "CAF": pd.DataFrame({
            "tenure": ["Combined"]
        }),
    }

    result = validate_tenure_values(workbook)

    assert result == {
        "Federal Public Service": ["Permanent"]
    }
    
def test_validate_department_names():
    """
    Check that known department names are accepted.
    """
    workbook = {
        "Departments": pd.DataFrame({
            "long_name_en": [
                "Canadian Armed Forces",
                "Royal Canadian Mounted Police - Members",
            ]
        }),
        "Federal Public Service": pd.DataFrame({
            "department": ["Canadian Armed Forces"]
        }),
        "RCMP": pd.DataFrame({
            "department": ["Royal Canadian Mounted Police - Members"]
        }),
        "CAF": pd.DataFrame({
            "department": ["Canadian Armed Forces"]
        }),
    }

    result = validate_department_names(workbook)

    assert result == {}
    
    
def test_validate_unknown_department():
    """
    Check that an unknown department name is reported.
    """
    workbook = {
        "Departments": pd.DataFrame({
            "long_name_en": ["Canadian Armed Forces"]
        }),
        "Federal Public Service": pd.DataFrame({
            "department": ["Unknown Department"]
        }),
        "RCMP": pd.DataFrame({
            "department": ["Canadian Armed Forces"]
        }),
        "CAF": pd.DataFrame({
            "department": ["Canadian Armed Forces"]
        }),
    }

    result = validate_department_names(workbook)

    assert result == {
        "Federal Public Service": ["Unknown Department"]
    }
    
def test_validate_headcount_values():
    """
    Check that valid and missing headcount values are accepted.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "headcount": [100, 200, pd.NA]
        }),
        "RCMP": pd.DataFrame({
            "headcount": [300]
        }),
        "CAF": pd.DataFrame({
            "headcount": [400]
        }),
    }

    result = validate_headcount_values(workbook)

    assert result == {}


def test_validate_invalid_headcount_values():
    """
    Check that negative and fractional headcount values are rejected.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "headcount": [100, -20, 25.5]
        }),
        "RCMP": pd.DataFrame({
            "headcount": [300]
        }),
        "CAF": pd.DataFrame({
            "headcount": [400]
        }),
    }

    result = validate_headcount_values(workbook)

    assert result == {
        "Federal Public Service": {
            "negative": 1,
            "fractional": 1,
        }
    }
    
def test_validate_fte_values():
    """
    Check that missing FTE is allowed and negative FTE is invalid.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "fte": [10.5, pd.NA, -2.0]
        })
    }

    result = validate_fte_values(workbook)

    assert result == {"negative": 1}
    
def test_validate_date_values():
    """
    Check that invalid YYYYMM values are rejected.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "date": [201503, 201513]
        }),
        "RCMP": pd.DataFrame({"date": [201504]}),
        "CAF": pd.DataFrame({"date": [201504]}),
    }

    result = validate_date_values(workbook)

    assert "Federal Public Service" in result
    
def test_validate_reference_data():
    """
    Check required reference names and uniqueness.
    """
    workbook = {
        "Departments": pd.DataFrame({
            "long_name_en": ["Department A", "Department A"],
            "long_name_fr": ["Ministère A", "Ministère A"],
        })
    }

    result = validate_reference_data(workbook)

    assert result["duplicate_long_name_en"] == 1
    
def test_validate_workforce_duplicates():
    """
    Check that duplicate workforce records are rejected.
    """
    row = {
        "date": 201503,
        "department": "Department A",
        "tenure": "Term",
    }

    workbook = {
        "Federal Public Service": pd.DataFrame([row, row]),
        "RCMP": pd.DataFrame([row]),
        "CAF": pd.DataFrame([row]),
    }

    result = validate_workforce_duplicates(workbook)

    assert "Federal Public Service" in result