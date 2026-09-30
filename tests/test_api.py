from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)

def get_test_department_id():
    """
    Return the ID of a department with known FTE data.
    """
    response = client.get("/api/departments")
    departments = response.json()["departments"]

    for department in departments:
        if (
            department["dept_long"]["en"]
            == "Administrative Tribunals Support Service of Canada"
        ):
            return department["dept_id"]

    raise AssertionError("Test department was not found.")
  

def test_list_departments():
    """
    Check the departments endpoint response structure.
    """
    response = client.get("/api/departments")

    assert response.status_code == 200

    data = response.json()

    assert "departments" in data
    assert len(data["departments"]) == 101

    department = data["departments"][0]

    assert "dept_id" in department
    assert "dept_long" in department
    assert "dept_short" in department

    assert "en" in department["dept_long"]
    assert "fr" in department["dept_long"]

    assert "en" in department["dept_short"]
    assert "fr" in department["dept_short"]
    
def test_get_department_fte():
    """
    Check that quarterly FTE data is returned.
    """
    department_id = get_test_department_id()

    response = client.get(
        f"/api/departments/{department_id}/fte"
    )

    assert response.status_code == 200

    data = response.json()

    assert "fte_per_quarter" in data
    assert len(data["fte_per_quarter"]) > 0
    
def test_get_department_fte_by_year():
    """
    Check that FTE data can be filtered by year.
    """
    department_id = get_test_department_id()

    response = client.get(
        f"/api/departments/{department_id}/fte?year=2020"
    )

    assert response.status_code == 200

    records = response.json()["fte_per_quarter"]

    assert len(records) == 4

    for record in records:
        assert record["year"] == 2020
        assert 1 <= record["quarter"] <= 4
        
def test_get_department_fte_by_tenure():
    """
    Check that FTE data can be filtered by tenure.
    """
    department_id = get_test_department_id()

    response = client.get(
        f"/api/departments/{department_id}/fte?tenure=Term"
    )

    assert response.status_code == 200
    assert "fte_per_quarter" in response.json()
    

def test_get_department_fte_by_year_and_tenure():
    """
    Check that year and tenure filters work together.
    """
    department_id = get_test_department_id()

    response = client.get(
        f"/api/departments/{department_id}/fte"
        "?year=2020&tenure=Term"
    )

    assert response.status_code == 200

    records = response.json()["fte_per_quarter"]

    for record in records:
        assert record["year"] == 2020
        
def test_get_department_fte_not_found():
    """
    Check that an unknown department returns 404.
    """
    response = client.get(
        "/api/departments/999999/fte"
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Department not found."
    }