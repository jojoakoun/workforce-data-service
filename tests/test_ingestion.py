from app.ingestion import read_workbook


def test_read_workbook():
    """
    Check that the expected workbook sheets can be read.
    """
    workbook = read_workbook("data/data.xlsx")

    assert "Federal Public Service" in workbook
    assert "RCMP" in workbook
    assert "CAF" in workbook
    assert "Departments" in workbook