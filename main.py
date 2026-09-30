from app.ingestion import read_workbook
from app.inspection import (
    print_sample_data,
    print_workbook_summary,
)
from app.processing import (
    process_departments,
    process_tenure,
    process_headcount,
    process_dates,
    process_duplicates,
    process_fte,
    process_reference_quality,
)
from app.validation import validate_workbook_structure

from app.database import get_connection
from app.loader import load_database
from app.transformation import prepare_workforce_records


DATA_FILE = "data/data.xlsx"


def main():
    """
    Run the Workforce Data Service data pipeline.
    """
    print("=== Workforce Data Service ===")

    print("\n[PIPELINE 1/12] Reading workbook...")
    workbook = read_workbook(DATA_FILE)

    print("\n[PIPELINE 2/12] Validating workbook structure...")
    validate_workbook_structure(workbook)

    print("\n[PIPELINE 3/12] Inspecting workbook...")
    print_workbook_summary(workbook)
    print_sample_data(workbook)

    print("\n[PIPELINE 4/12] Processing tenure...")
    workbook = process_tenure(workbook)

    print("\n[PIPELINE 5/12] Processing departments...")
    workbook = process_departments(workbook)
    
    print("\n[PIPELINE 6/12] Processing headcount...")
    workbook = process_headcount(workbook)
    
    print("\n[PIPELINE 7/12] Processing FTE...")
    workbook = process_fte(workbook)

    print("\n[PIPELINE 8/12] Processing dates...")
    workbook = process_dates(workbook)

    print("\n[PIPELINE 9/12] Processing department reference...")
    workbook = process_reference_quality(workbook)

    print("\n[PIPELINE 10/12] Checking duplicates...")
    workbook = process_duplicates(workbook)
    
    print("\n[PIPELINE 11/12] Preparing database records...")
    workforce_records = prepare_workforce_records(workbook)

    print("\n[PIPELINE 12/12] Loading PostgreSQL database...")

    with get_connection() as connection:
      load_database(
          connection,
          workbook,
          workforce_records,
      )

    print("\n=== Pipeline completed successfully ===")


if __name__ == "__main__":
    main()