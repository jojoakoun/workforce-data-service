WORKFORCE_SHEETS = [
    "Federal Public Service",
    "RCMP",
    "CAF",
]

DEPARTMENT_NAME_CORRECTIONS = {
    "Privy Council Officee": "Privy Council Office",
}


def clean_text(value):
    """
    Remove extra whitespace from a text value.

    Keep missing values unchanged.
    """
    if not isinstance(value, str):
        return value

    return " ".join(value.split())


def clean_tenure_values(workbook):
    """
    Clean tenure values in all workforce sheets.

    Return the workbook with cleaned tenure values.
    """
    for sheet_name in WORKFORCE_SHEETS:
        workbook[sheet_name]["tenure"] = (
            workbook[sheet_name]["tenure"].map(clean_text)
        )

    return workbook


def clean_workforce_department_names(workbook):
    """
    Clean department names in all workforce sheets.

    Return the workbook with cleaned department names.
    """
    for sheet_name in WORKFORCE_SHEETS:
        workbook[sheet_name]["department"] = (
            workbook[sheet_name]["department"].map(clean_text)
        )

    return workbook


def clean_reference_department_names(workbook):
    """
    Clean text values in the department reference.

    Keep missing values unchanged.
    """
    columns = [
        "long_name_en",
        "long_name_fr",
        "short_name_en",
        "short_name_fr",
    ]

    for column in columns:
        workbook["Departments"][column] = (
            workbook["Departments"][column].map(clean_text)
        )

    return workbook

def correct_known_department_names(workbook):
    """
    Correct known department name errors in workforce sheets.

    Only corrections confirmed against the reference data are used.
    """
    for sheet_name in WORKFORCE_SHEETS:
        workbook[sheet_name]["department"] = (
            workbook[sheet_name]["department"].replace(
                DEPARTMENT_NAME_CORRECTIONS
            )
        )

    return workbook
  
def clean_headcount_values(workbook):
    """
    Replace negative headcount values with missing values.

    Keep existing missing values unchanged.
    """
    for sheet_name in WORKFORCE_SHEETS:
        dataframe = workbook[sheet_name]

        dataframe["headcount"] = dataframe["headcount"].mask(
            dataframe["headcount"] < 0
        )

    return workbook
  
def clean_reference_duplicates(workbook):
    """
    Remove exact duplicate rows from the department reference.

    Keep the first occurrence of each identical row.
    """
    workbook["Departments"] = (
        workbook["Departments"]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    return workbook