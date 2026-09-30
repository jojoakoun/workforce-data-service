import pandas as pd


DATA_FILE = "data/data.xlsx"


def normalize_name(name):
    # Normalize whitespace for comparison without changing the source data.
    return " ".join(name.split())


def print_department_quality():
    # Identify department naming issues before defining cleaning rules.
    workbook = pd.ExcelFile(DATA_FILE)
    departments = pd.read_excel(workbook, sheet_name="Departments")

    reference_names = {
        normalize_name(name)
        for name in departments["long_name_en"].dropna()
    }

    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet_name)

        if "department" not in df.columns:
            continue

        source_names = df["department"].dropna().unique()

        whitespace_issues = [
            name for name in source_names
            if name != normalize_name(name)
        ]

        unmatched = [
            normalize_name(name)
            for name in source_names
            if normalize_name(name) not in reference_names
        ]

        print(f"\n=== {sheet_name} ===")
        print(f"Whitespace issues: {whitespace_issues}")
        print(f"Unmatched departments: {unmatched}")


def print_tenure_quality():
    # Show exact tenure values so hidden whitespace remains visible.
    workbook = pd.ExcelFile(DATA_FILE)

    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet_name)

        if "tenure" not in df.columns:
            continue

        print(f"\n=== {sheet_name} tenure ===")

        for value in df["tenure"].dropna().unique():
            count = (df["tenure"] == value).sum()
            print(f"{value!r}: {count}")

        print(f"Missing values: {df['tenure'].isna().sum()}")


def print_headcount_quality():
    # Inspect problematic headcount rows before deciding how to handle them.
    workbook = pd.ExcelFile(DATA_FILE)

    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet_name)

        if "headcount" not in df.columns:
            continue

        issues = df[
            df["headcount"].isna() | (df["headcount"] < 0)
        ]

        print(f"\n=== {sheet_name} headcount issues ===")
        print(issues)


def print_fte_quality():
    # Inspect problematic FTE rows before deciding how to handle them.
    workbook = pd.ExcelFile(DATA_FILE)

    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet_name)

        if "fte" not in df.columns:
            continue

        issues = df[
            df["fte"].isna() | (df["fte"] < 0)
        ]

        print(f"\n=== {sheet_name} FTE issues ===")
        print(issues)


def print_date_quality():
    # Verify that date values use a valid YYYYMM format.
    workbook = pd.ExcelFile(DATA_FILE)

    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet_name)

        if "date" not in df.columns:
            continue

        dates = df["date"].dropna().astype(int)
        months = dates % 100

        invalid_dates = dates[
            (months < 1) | (months > 12)
        ]

        print(f"\n=== {sheet_name} date ===")
        print(f"Min: {dates.min()}")
        print(f"Max: {dates.max()}")
        print(f"Missing values: {df['date'].isna().sum()}")
        print(f"Invalid months: {len(invalid_dates)}")


def print_reference_quality():
    # Check whether the department reference data is complete and unique.
    departments = pd.read_excel(DATA_FILE, sheet_name="Departments")

    print("\n=== Departments reference quality ===")
    print("Missing values:")
    print(departments.isna().sum())

    print(f"\nDuplicate rows: {departments.duplicated().sum()}")

    if departments.duplicated().any():
        print("\nDuplicate records:")
        print(departments[departments.duplicated(keep=False)])


def print_workforce_duplicates():
    # Check whether workforce datasets contain exact duplicate records.
    workbook = pd.ExcelFile(DATA_FILE)

    for sheet_name in workbook.sheet_names:
        if sheet_name == "Departments":
            continue

        df = pd.read_excel(workbook, sheet_name=sheet_name)

        print(f"\n=== {sheet_name} duplicates ===")
        print(f"Duplicate rows: {df.duplicated().sum()}")

