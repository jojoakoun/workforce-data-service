def get_departments(connection):
    """
    Return all departments in the API response format.
    """
    sql = """
        SELECT
            id,
            long_name_en,
            long_name_fr,
            short_name_en,
            short_name_fr
        FROM departments
        ORDER BY long_name_en;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql)
        rows = cursor.fetchall()

    departments = []

    for row in rows:
        departments.append({
            "dept_id": row[0],
            "dept_long": {
                "en": row[1],
                "fr": row[2],
            },
            "dept_short": {
                "en": row[3],
                "fr": row[4],
            },
        })

    return departments
  
  
def get_department_fte(
    connection,
    department_id,
    year=None,
    tenure=None,
):
    """
    Return quarterly average FTE values for one department.

    Apply optional year and tenure filters.
    """
    sql = """
        SELECT
            EXTRACT(YEAR FROM period)::INTEGER AS year,
            EXTRACT(QUARTER FROM period)::INTEGER AS quarter,

            COALESCE(
                AVG(fte) FILTER (
                    WHERE tenure = 'Indeterminate'
                ),
                0
            ) AS indeterminate,

            COALESCE(
                AVG(fte) FILTER (
                    WHERE tenure = 'Term'
                ),
                0
            ) AS term,

            COALESCE(
                AVG(fte) FILTER (
                    WHERE tenure = 'Casual'
                ),
                0
            ) AS casual,

            COALESCE(
                AVG(fte) FILTER (
                    WHERE tenure = 'Student'
                ),
                0
            ) AS student,

            COALESCE(
                AVG(fte) FILTER (
                    WHERE tenure = 'Missing'
                ),
                0
            ) AS missing

        FROM workforce_records
        WHERE department_id = %s
          AND fte IS NOT NULL
    """

    parameters = [department_id]

    if year is not None:
        sql += """
            AND EXTRACT(YEAR FROM period) = %s
        """
        parameters.append(year)

    if tenure is not None:
        sql += """
            AND tenure = %s
        """
        parameters.append(tenure)

    sql += """
        GROUP BY
            EXTRACT(YEAR FROM period),
            EXTRACT(QUARTER FROM period)

        ORDER BY year, quarter;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, parameters)
        rows = cursor.fetchall()

    return [
        {
            "year": row[0],
            "quarter": row[1],
            "indeterminate": round(float(row[2]), 2),
            "term": round(float(row[3]), 2),
            "casual": round(float(row[4]), 2),
            "student": round(float(row[5]), 2),
            "missing": round(float(row[6]), 2),
        }
        for row in rows
    ]
  
def department_exists(connection, department_id):
    """
    Check whether a department exists.
    """
    sql = """
        SELECT 1
        FROM departments
        WHERE id = %s;
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, (department_id,))
        return cursor.fetchone() is not None