from fastapi import FastAPI, HTTPException

from app.database import get_connection
from app.queries import (
  department_exists,
  get_department_fte,
  get_departments,
)


app = FastAPI(
    title="Workforce Data Service",
    version="1.0.0",
)


@app.get("/api/departments")
def list_departments():
    """
    Return all departments.
    """
    with get_connection() as connection:
        departments = get_departments(connection)

    return {
        "departments": departments
    }
    
@app.get("/api/departments/{department_id}/fte")
def department_fte(
    department_id: int,
    year: int | None = None,
    tenure: str | None = None,
):
    """
    Return quarterly FTE values for one department.

    Optionally filter by year and tenure.
    """
    with get_connection() as connection:
        if not department_exists(connection, department_id):
            raise HTTPException(
                status_code=404,
                detail="Department not found.",
            )

        fte_per_quarter = get_department_fte(
            connection,
            department_id,
            year,
            tenure,
        )

    return {
        "fte_per_quarter": fte_per_quarter
    }