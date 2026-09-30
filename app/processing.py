from app.cleaning import (
    DEPARTMENT_NAME_CORRECTIONS,
    clean_reference_department_names,
    clean_tenure_values,
    clean_workforce_department_names,
    correct_known_department_names,
    clean_headcount_values,
    clean_reference_duplicates
)
from app.inspection import (
    print_department_whitespace_issues,
    print_reference_department_whitespace_issues,
    print_tenure_values,print_headcount_issues,
    print_date_summary,
    print_duplicate_issues,
    print_fte_issues,
    print_reference_quality,
)
from app.validation import (
    validate_department_names,
    validate_tenure_values,
    validate_headcount_values,
    validate_date_values,
    validate_fte_values,
    validate_reference_data,
    validate_workforce_duplicates,
)


def process_tenure(workbook):
    """
    Inspect, clean, and validate tenure values.

    Return the workbook with cleaned tenure values.
    """
    print("\n=== TENURE PROCESSING ===")

    print("[TENURE 1/3] Inspecting raw tenure values...")
    print_tenure_values(workbook, "BEFORE CLEANING")

    print("\n[TENURE 2/3] Cleaning tenure values...")
    workbook = clean_tenure_values(workbook)
    print_tenure_values(workbook, "AFTER CLEANING")

    print("\n[TENURE 3/3] Validating tenure values...")
    invalid_tenure = validate_tenure_values(workbook)

    if invalid_tenure:
        raise ValueError(
            f"Invalid tenure values: {invalid_tenure}"
        )

    print("[TENURE] All tenure values are valid.")

    return workbook


def process_departments(workbook):
    """
    Clean and validate department names.

    Workforce department names come from the Federal Public Service,
    RCMP, and CAF sheets.

    Valid department names come from Departments.long_name_en.
    """
    print("\n=== DEPARTMENT PROCESSING ===")

    print(
        "\n[DEPARTMENT 1/6] "
        "Inspecting workforce department names..."
    )
    print(
        "Source sheets: "
        "Federal Public Service, RCMP, CAF"
    )

    print_department_whitespace_issues(
        workbook,
        "BEFORE CLEANING",
    )

    print(
        "\n[DEPARTMENT 2/6] "
        "Inspecting reference department names..."
    )
    print("Reference: Departments.long_name_en")

    print_reference_department_whitespace_issues(
        workbook,
        "BEFORE CLEANING",
    )

    print(
        "\n[DEPARTMENT 3/6] "
        "Cleaning whitespace on both sides..."
    )

    workbook = clean_workforce_department_names(workbook)
    workbook = clean_reference_department_names(workbook)

    print(
        "\n[DEPARTMENT 4/6] "
        "Applying confirmed department corrections..."
    )

    for wrong_name, correct_name in DEPARTMENT_NAME_CORRECTIONS.items():
        print(
            f"- {wrong_name!r} "
            f"-> {correct_name!r}"
        )

    workbook = correct_known_department_names(workbook)

    print(
        "\n[DEPARTMENT 5/6] "
        "Checking names after cleaning..."
    )

    print_department_whitespace_issues(
        workbook,
        "AFTER CLEANING",
    )

    print_reference_department_whitespace_issues(
        workbook,
        "AFTER CLEANING",
    )

    print(
        "\n[DEPARTMENT 6/6] "
        "Matching workforce departments "
        "against Departments.long_name_en..."
    )

    unknown_departments = validate_department_names(workbook)

    if unknown_departments:
        raise ValueError(
            f"Unknown departments: {unknown_departments}"
        )

    print(
        "[DEPARTMENT] All workforce department names "
        "match the reference."
    )

    return workbook
def process_headcount(workbook):
    """
    Inspect, clean, and validate headcount values.

    Return the workbook with cleaned headcount values.
    """
    print("\n=== HEADCOUNT PROCESSING ===")

    print("\n[HEADCOUNT 1/4] Inspecting raw values...")
    print_headcount_issues(workbook)

    print("\n[HEADCOUNT 2/4] Cleaning invalid values...")
    workbook = clean_headcount_values(workbook)

    print("\n[HEADCOUNT 3/4] Inspecting cleaned values...")
    print_headcount_issues(workbook)

    print("\n[HEADCOUNT 4/4] Validating headcount values...")
    invalid_headcount = validate_headcount_values(workbook)

    if invalid_headcount:
        raise ValueError(
            f"Invalid headcount values: {invalid_headcount}"
        )

    print("[HEADCOUNT] All headcount values are valid.")

    return workbook
  
def process_fte(workbook):
    """
    Inspect and validate Federal Public Service FTE values.
    """
    print("\n=== FTE PROCESSING ===")

    print("\n[FTE 1/2] Inspecting FTE values...")
    print_fte_issues(workbook)

    print("\n[FTE 2/2] Validating FTE values...")
    invalid_fte = validate_fte_values(workbook)

    if invalid_fte:
        raise ValueError(f"Invalid FTE values: {invalid_fte}")

    print("[FTE] FTE values are valid.")

    return workbook
  
def process_dates(workbook):
    """
    Inspect and validate workforce date values.
    """
    print("\n=== DATE PROCESSING ===")

    print("\n[DATE 1/2] Inspecting date values...")
    print_date_summary(workbook)

    print("\n[DATE 2/2] Validating YYYYMM values...")
    invalid_dates = validate_date_values(workbook)

    if invalid_dates:
        raise ValueError(f"Invalid dates: {invalid_dates}")

    print("[DATE] All workforce dates are valid YYYYMM values.")

    return workbook
  

def process_reference_quality(workbook):
    """
    Inspect, clean, and validate the department reference.
    """
    print("\n=== REFERENCE PROCESSING ===")

    print("\n[REFERENCE 1/4] Inspecting raw reference...")
    print_reference_quality(workbook)

    print("\n[REFERENCE 2/4] Removing exact duplicates...")
    workbook = clean_reference_duplicates(workbook)

    print("\n[REFERENCE 3/4] Inspecting cleaned reference...")
    print_reference_quality(workbook)

    print("\n[REFERENCE 4/4] Validating reference...")
    issues = validate_reference_data(workbook)

    if issues:
        raise ValueError(f"Invalid department reference: {issues}")

    print("[REFERENCE] Department reference is valid.")

    return workbook
  
def process_duplicates(workbook):
    """
    Inspect and validate workforce duplicate records.
    """
    print("\n=== DUPLICATE PROCESSING ===")

    print("\n[DUPLICATES 1/2] Inspecting workforce records...")
    print_duplicate_issues(workbook)

    print("\n[DUPLICATES 2/2] Validating duplicates...")
    issues = validate_workforce_duplicates(workbook)

    if issues:
        raise ValueError(f"Duplicate workforce records: {issues}")

    print("[DUPLICATES] No workforce duplicates found.")

    return workbook