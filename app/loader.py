import pandas as pd


def to_database_value(value):
    """
    Convert pandas missing values to Python None.
    """
    if pd.isna(value):
        return None

    return value
  

def load_database(
    connection,
    workbook,
    workforce_records,
):
    """
    Load departments and workforce records into PostgreSQL.
    """
    print("\n=== DATABASE LOAD ===")

    print("[DATABASE 1/3] Loading departments...")
    load_departments(
        connection,
        workbook["Departments"],
    )

    print("[DATABASE 2/3] Resolving department IDs...")
    department_ids = get_department_ids(connection)

    print("[DATABASE 3/3] Loading workforce records...")
    load_workforce_records(
        connection,
        workforce_records,
        department_ids,
    )

    print("[DATABASE] Load completed.")


def load_departments(connection, departments):
    """
    Load cleaned department reference data into PostgreSQL.
    """
    sql = """
        INSERT INTO departments (
            long_name_en,
            long_name_fr,
            short_name_en,
            short_name_fr
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (long_name_en) DO NOTHING;
    """

    with connection.cursor() as cursor:
        for _, row in departments.iterrows():
            cursor.execute(
                sql,
                (
                    to_database_value(row["long_name_en"]),
                    to_database_value(row["long_name_fr"]),
                    to_database_value(row["short_name_en"]),
                    to_database_value(row["short_name_fr"]),
                ),
            )

    connection.commit()
    
def get_department_ids(connection):
    """
    Return department IDs indexed by English department name.
    """
    sql = """
        SELECT id, long_name_en
        FROM departments;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    return {
        long_name_en: department_id
        for department_id, long_name_en in rows
    }
    
def load_workforce_records(
    connection,
    workforce_records,
    department_ids,
):
    """
    Load prepared workforce records into PostgreSQL.
    """
    sql = """
        INSERT INTO workforce_records (
            period,
            source,
            department_id,
            tenure,
            headcount,
            fte
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
    """

    with connection.cursor() as cursor:
        for _, row in workforce_records.iterrows():
            department_id = department_ids[row["department"]]

            cursor.execute(
                sql,
                (
                    row["period"],
                    row["source"],
                    department_id,
                    to_database_value(row["tenure"]),
                    to_database_value(row["headcount"]),
                    to_database_value(row["fte"]),
                ),
            )

    connection.commit()