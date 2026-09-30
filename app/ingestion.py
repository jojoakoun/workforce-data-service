import pandas as pd


def read_workbook(file_path):
    """
    Read all sheets from the workforce Excel file.

    Return the sheets in a dictionary.
    """
    print(f"[READ] Opening file: {file_path}")

    workbook = pd.read_excel(file_path,sheet_name=None)

    print(f"[READ] Sheets found: {list(workbook.keys())}")

    return workbook