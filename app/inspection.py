WORKFORCE_SHEETS = [
    "Federal Public Service",
    "RCMP",
    "CAF",
]


def print_workbook_summary(workbook):
    """
    Print the number of rows and columns in each workbook sheet.
    """
    print("\n[INFO] Workbook summary:")

    for sheet_name, dataframe in workbook.items():
        row_count = len(dataframe)
        column_count = len(dataframe.columns)

        print(
            f"- {sheet_name}: "
            f"{row_count} rows, "
            f"{column_count} columns"
        )


def print_sample_data(workbook):
    """
    Print the first three rows from each workbook sheet.
    """
    print("\n[INFO] Sample data:")

    for sheet_name, dataframe in workbook.items():
        print(f"\n--- {sheet_name} ---")
        print(dataframe.head(3))


def print_tenure_values(workbook, stage):
    """
    Print tenure values for all workforce sheets.

    Use repr() so hidden whitespace remains visible.
    """
    print(f"\n[INFO] Tenure values - {stage}:")

    for sheet_name in WORKFORCE_SHEETS:
        print(f"\n--- {sheet_name} ---")

        counts = (
            workbook[sheet_name]["tenure"]
            .value_counts(dropna=False)
        )

        for value, count in counts.items():
            print(f"{repr(value)}: {count}")


def print_department_whitespace_issues(workbook, stage):
    """
    Print whitespace problems in workforce department names.
    """
    print(
        f"\n[INFO] Workforce department whitespace "
        f"- {stage}:"
    )

    for sheet_name in WORKFORCE_SHEETS:
        print(f"\n--- {sheet_name} ---")

        values = (
            workbook[sheet_name]["department"]
            .dropna()
            .unique()
        )

        issues = []

        for value in values:
            cleaned_value = " ".join(value.split())

            if value != cleaned_value:
                issues.append(value)

        if issues:
            for value in issues:
                print(repr(value))
        else:
            print("No whitespace issues found.")


def print_reference_department_whitespace_issues(
    workbook,
    stage,
):
    """
    Print whitespace problems in reference department names.
    """
    print(
        f"\n[INFO] Reference department whitespace "
        f"- {stage}:"
    )

    values = (
        workbook["Departments"]["long_name_en"]
        .dropna()
        .unique()
    )

    issues = []

    for value in values:
        cleaned_value = " ".join(value.split())

        if value != cleaned_value:
            issues.append(value)

    if issues:
        for value in issues:
            print(repr(value))
    else:
        print("No whitespace issues found.")
        
        
def print_headcount_issues(workbook):
    """
    Print missing and negative headcount values.

    Check all workforce sheets without changing the data.
    """
    print("\n[INFO] Headcount issues:")

    for sheet_name in WORKFORCE_SHEETS:
        dataframe = workbook[sheet_name]

        missing_count = dataframe["headcount"].isna().sum()
        missing_rows = dataframe[dataframe["headcount"].isna()]

        negative_rows = dataframe[
            dataframe["headcount"] < 0
        ]
        
        fractional_rows = dataframe[
            dataframe["headcount"].notna()
            & (dataframe["headcount"] % 1 != 0)
        ]

        print(f"\n--- {sheet_name} ---")
        print(f"Missing values: {missing_count}")
        
        if not missing_rows.empty:
          print("Rows with missing headcount:")
          print(missing_rows)
        print(f"Negative values: {len(negative_rows)}")

        if not negative_rows.empty:
            print(negative_rows)
            
        print(f"Fractional values: {len(fractional_rows)}")

        if not fractional_rows.empty:
            print("Rows with fractional headcount:")
            print(fractional_rows)
            
def print_fte_issues(workbook):
    """
    Print missing and negative FTE values.

    FTE exists only in the Federal Public Service sheet.
    """
    dataframe = workbook["Federal Public Service"]

    missing_count = dataframe["fte"].isna().sum()
    negative_rows = dataframe[dataframe["fte"] < 0]

    print("\n[INFO] FTE issues:")
    print("\n--- Federal Public Service ---")
    print(f"Missing values: {missing_count}")
    print(f"Negative values: {len(negative_rows)}")

    if not negative_rows.empty:
        print(negative_rows)

    print("\nRCMP and CAF have no FTE column in the source.")
    
def print_date_summary(workbook):
    """
    Print missing values and date ranges for workforce sheets.
    """
    print("\n[INFO] Date summary:")

    for sheet_name in WORKFORCE_SHEETS:
        values = workbook[sheet_name]["date"]
        non_missing = values.dropna()

        print(f"\n--- {sheet_name} ---")
        print(f"Missing values: {values.isna().sum()}")

        if not non_missing.empty:
            print(
                f"Range: {non_missing.min()} "
                f"to {non_missing.max()}"
            )
            
def print_reference_quality(workbook):
    """
    Print data-quality information for the department reference.
    """
    dataframe = workbook["Departments"]

    print("\n[INFO] Department reference quality:")
    print(f"Rows: {len(dataframe)}")
    print(f"Exact duplicates: {dataframe.duplicated().sum()}")
    print(
        "Missing long_name_en: "
        f"{dataframe['long_name_en'].isna().sum()}"
    )
    print(
        "Missing long_name_fr: "
        f"{dataframe['long_name_fr'].isna().sum()}"
    )
    print(
        "Missing short_name_en: "
        f"{dataframe['short_name_en'].isna().sum()}"
    )
    print(
        "Missing short_name_fr: "
        f"{dataframe['short_name_fr'].isna().sum()}"
    )
    
def print_duplicate_issues(workbook):
    """
    Print exact and business-key duplicates in workforce sheets.
    """
    print("\n[INFO] Workforce duplicate check:")

    for sheet_name in WORKFORCE_SHEETS:
        dataframe = workbook[sheet_name]

        exact_count = dataframe.duplicated().sum()

        key_count = dataframe.duplicated(
            subset=["date", "department", "tenure"]
        ).sum()

        print(f"\n--- {sheet_name} ---")
        print(f"Exact duplicates: {exact_count}")
        print(f"Business-key duplicates: {key_count}")