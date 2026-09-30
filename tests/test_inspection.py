import pandas as pd

from app.inspection import (
    print_sample_data,
    print_tenure_values,
    print_workbook_summary,
    print_department_whitespace_issues,
    print_reference_department_whitespace_issues,
    print_headcount_issues,
    print_date_summary,
    print_duplicate_issues,
    print_fte_issues,
    print_reference_quality
)

def test_print_workbook_summary(capsys):
    """
    Check that the workbook summary shows rows and columns.
    """
    workbook = {
        "CAF": pd.DataFrame({
            "date": [202501, 202502],
            "headcount": [100, 200],
        })
    }

    print_workbook_summary(workbook)

    output = capsys.readouterr().out

    assert "CAF: 2 rows, 2 columns" in output
    

def test_print_sample_data(capsys):
    """
    Check that sample rows are printed for each sheet.
    """
    workbook = {
        "CAF": pd.DataFrame({
            "date": [202501, 202502, 202503, 202504],
            "headcount": [100, 200, 300, 400],
        })
    }

    print_sample_data(workbook)

    output = capsys.readouterr().out

    assert "[INFO] Sample data:" in output
    assert "--- CAF ---" in output
    assert "202501" in output
    assert "202503" in output
    
def test_print_tenure_values(capsys):
    """
    Check that tenure values and counts are printed.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "tenure": ["Term", "Term", "Casual"]
        }),
        "RCMP": pd.DataFrame({
            "tenure": ["Combined"]
        }),
        "CAF": pd.DataFrame({
            "tenure": ["Combined"]
        }),
    }

    print_tenure_values(workbook, "TEST")

    output = capsys.readouterr().out

    assert "[INFO] Tenure values - TEST:" in output
    assert "Term" in output
    assert "Casual" in output
    assert "Combined" in output
       
def test_print_department_whitespace_issues(capsys):
    """
    Check that department names with extra spaces are reported.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "department": [
                "Department A",
                " Department  B ",
            ]
        }),
        "RCMP": pd.DataFrame({
            "department": ["RCMP"]
        }),
        "CAF": pd.DataFrame({
            "department": ["CAF"]
        }),
    }

    print_department_whitespace_issues(workbook,"TEST")

    output = capsys.readouterr().out

    assert "' Department  B '" in output
    assert "No whitespace issues found." in output
    
def test_print_reference_department_whitespace_issues(capsys):
    """
    Check that whitespace issues in the department reference are reported.
    """
    workbook = {
        "Departments": pd.DataFrame({
            "long_name_en": [
                "Canadian Armed Forces ",
                "Global  Affairs Canada",
            ]
        })
    }

    print_reference_department_whitespace_issues(workbook,"TEST")

    output = capsys.readouterr().out

    assert "'Canadian Armed Forces '" in output
    assert "'Global  Affairs Canada'" in output
    
def test_print_headcount_issues(capsys):
    """
    Check that missing and negative headcount values are reported.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "headcount": [100, -20, 25.5, pd.NA]
        }),
        "RCMP": pd.DataFrame({
            "headcount": [200]
        }),
        "CAF": pd.DataFrame({
            "headcount": [300]
        }),
    }

    print_headcount_issues(workbook)

    output = capsys.readouterr().out

    assert "Missing values: 1" in output
    assert "Negative values: 1" in output
    assert "-20" in output
    assert "Rows with missing headcount:" in output
    assert "Fractional values: 1" in output
    assert "25.5" in output
    
def test_print_fte_issues(capsys):
    """
    Check that FTE issues are reported.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "fte": [10.5, pd.NA, -2]
        })
    }

    print_fte_issues(workbook)

    output = capsys.readouterr().out

    assert "Missing values: 1" in output
    assert "Negative values: 1" in output
    
def test_print_date_summary(capsys):
    """
    Check that workforce date ranges are reported.
    """
    workbook = {
        "Federal Public Service": pd.DataFrame({
            "date": [201503, 201504]
        }),
        "RCMP": pd.DataFrame({"date": [201504]}),
        "CAF": pd.DataFrame({"date": [201504]}),
    }

    print_date_summary(workbook)

    output = capsys.readouterr().out

    assert "201503 to 201504" in output
    
def test_print_reference_quality(capsys):
    """
    Check that reference quality counts are reported.
    """
    workbook = {
        "Departments": pd.DataFrame({
            "long_name_en": ["A", "A"],
            "long_name_fr": ["A", "A"],
            "short_name_en": [pd.NA, pd.NA],
            "short_name_fr": [pd.NA, pd.NA],
        })
    }

    print_reference_quality(workbook)

    output = capsys.readouterr().out

    assert "Exact duplicates: 1" in output
    
def test_print_duplicate_issues(capsys):
    """
    Check that workforce duplicates are reported.
    """
    row = {
        "date": 201503,
        "department": "A",
        "tenure": "Term",
    }

    workbook = {
        "Federal Public Service": pd.DataFrame([row, row]),
        "RCMP": pd.DataFrame([row]),
        "CAF": pd.DataFrame([row]),
    }

    print_duplicate_issues(workbook)

    output = capsys.readouterr().out

    assert "Exact duplicates: 1" in output