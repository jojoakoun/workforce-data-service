import pandas as pd

REQUIRED_SHEETS = [
    "Federal Public Service",
    "RCMP",
    "CAF",
    "Departments",
]

REQUIRED_COLUMNS = {
    "Federal Public Service": [
        "date",
        "tenure",
        "department",
        "headcount",
        "fte",
    ],
    "RCMP": [
        "date",
        "tenure",
        "department",
        "headcount",
    ],
    "CAF": [
        "date",
        "tenure",
        "department",
        "headcount",
    ],
    "Departments": [
        "long_name_en",
        "long_name_fr",
        "short_name_en",
        "short_name_fr",
    ],
}

VALID_TENURE_VALUES = {
    "Federal Public Service": [
        "Indeterminate",
        "Term",
        "Student",
        "Casual",
        "Missing",
    ],
    "RCMP": ["Combined"],
    "CAF": ["Combined"],
}


def validate_sheets(workbook):
    """
    Check that all required sheets are present.

    Return a list of missing sheet names.
    """
    missing_sheets = []

    for sheet_name in REQUIRED_SHEETS:
        if sheet_name not in workbook:
            missing_sheets.append(sheet_name)

    return missing_sheets


def validate_columns(workbook):
    """
    Check that each sheet contains its required columns.

    Return missing columns grouped by sheet name.
    """
    missing_columns = {}

    for sheet_name, required_columns in REQUIRED_COLUMNS.items():
        missing = []

        for column_name in required_columns:
            if column_name not in workbook[sheet_name].columns:
                missing.append(column_name)

        if missing:
            missing_columns[sheet_name] = missing

    return missing_columns


def validate_workbook_structure(workbook):
    """
    Validate the required workbook sheets and columns.

    Raise an error when the workbook structure is invalid.
    """
    print("[VALIDATE] Checking workbook structure...")

    missing_sheets = validate_sheets(workbook)

    if missing_sheets:
        raise ValueError(
            f"Missing sheets: {missing_sheets}"
        )

    missing_columns = validate_columns(workbook)

    if missing_columns:
        raise ValueError(
            f"Missing columns: {missing_columns}"
        )

    print("[VALIDATE] Workbook structure is valid.")

    return True


def validate_tenure_values(workbook):
    """
    Check tenure values in all workforce sheets.

    Missing tenure values are allowed.
    """
    invalid_values = {}

    for sheet_name, valid_values in VALID_TENURE_VALUES.items():
        values = (
            workbook[sheet_name]["tenure"]
            .dropna()
            .unique()
        )

        invalid = []

        for value in values:
            if value not in valid_values:
                invalid.append(value)

        if invalid:
            invalid_values[sheet_name] = invalid

    return invalid_values


def validate_department_names(workbook):
    """
    Check workforce departments against the reference sheet.

    Return unknown department names grouped by sheet.
    """
    reference_names = set(
        workbook["Departments"]["long_name_en"]
        .dropna()
        .unique()
    )

    unknown_departments = {}

    workforce_sheets = [
        "Federal Public Service",
        "RCMP",
        "CAF",
    ]

    for sheet_name in workforce_sheets:
        values = (
            workbook[sheet_name]["department"]
            .dropna()
            .unique()
        )

        unknown = []

        for department in values:
            if department not in reference_names:
                unknown.append(department)

        if unknown:
            unknown_departments[sheet_name] = unknown

    return unknown_departments
  

def validate_headcount_values(workbook):
    """
    Check headcount values in all workforce sheets.

    Missing values are allowed.
    Negative and fractional values are invalid.
    """
    workforce_sheets = [
        "Federal Public Service",
        "RCMP",
        "CAF",
    ]

    invalid_values = {}

    for sheet_name in workforce_sheets:
        headcount = workbook[sheet_name]["headcount"].dropna()

        negative_count = (headcount < 0).sum()
        fractional_count = (headcount % 1 != 0).sum()

        if negative_count or fractional_count:
            invalid_values[sheet_name] = {
                "negative": int(negative_count),
                "fractional": int(fractional_count),
            }

    return invalid_values
  
  
def validate_fte_values(workbook):
    """
    Check FTE values in the Federal Public Service sheet.

    Missing values are allowed. Negative values are invalid.
    """
    fte = (
        workbook["Federal Public Service"]["fte"]
        .dropna()
    )

    negative_count = int((fte < 0).sum())

    if negative_count:
        return {"negative": negative_count}

    return {}
  
def validate_date_values(workbook):
    """
    Check that workforce dates use valid YYYYMM values.
    """
    workforce_sheets = [
        "Federal Public Service",
        "RCMP",
        "CAF",
    ]

    invalid_dates = {}

    for sheet_name in workforce_sheets:
        invalid = []

        for value in workbook[sheet_name]["date"]:
            if pd.isna(value):
                invalid.append(value)
                continue

            try:
                number = float(value)
            except (TypeError, ValueError):
                invalid.append(value)
                continue

            if not number.is_integer():
                invalid.append(value)
                continue

            period = int(number)
            month = period % 100

            if len(str(period)) != 6 or not 1 <= month <= 12:
                invalid.append(value)

        if invalid:
            invalid_dates[sheet_name] = invalid

    return invalid_dates
  

def validate_reference_data(workbook):
    """
    Check required department reference values and uniqueness.
    """
    dataframe = workbook["Departments"]

    issues = {}

    missing_en = dataframe["long_name_en"].isna().sum()
    missing_fr = dataframe["long_name_fr"].isna().sum()
    duplicate_en = dataframe["long_name_en"].duplicated().sum()

    if missing_en:
        issues["missing_long_name_en"] = int(missing_en)

    if missing_fr:
        issues["missing_long_name_fr"] = int(missing_fr)

    if duplicate_en:
        issues["duplicate_long_name_en"] = int(duplicate_en)

    return issues
  

def validate_workforce_duplicates(workbook):
    """
    Check workforce sheets for duplicate records.
    """
    workforce_sheets = [
        "Federal Public Service",
        "RCMP",
        "CAF",
    ]

    issues = {}

    for sheet_name in workforce_sheets:
        dataframe = workbook[sheet_name]

        exact = dataframe.duplicated().sum()
        key = dataframe.duplicated(
            subset=["date", "department", "tenure"]
        ).sum()

        if exact or key:
            issues[sheet_name] = {
                "exact": int(exact),
                "business_key": int(key),
            }

    return issues