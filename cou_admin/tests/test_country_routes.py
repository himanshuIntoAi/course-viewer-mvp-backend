import pytest
import requests

BASE_URL = "http://localhost:8000"

id = 204
name = "Test11"

# Test for creating a new country
def test_add_country():
    country_data = {
        "id": id,
        "name": name,
        "created_by": 1,
        "updated_by": 1,
        "active": True
    }
    response = requests.post(f"{BASE_URL}/api/v1/countries/", json=country_data)
    assert response.status_code == 200
    assert response.json()["name"] == name


# Test for fetching a country by ID
def test_get_country():
    country_id = id
    response = requests.get(f"{BASE_URL}/api/v1/countries/{country_id}")
    assert response.status_code == 200
    assert response.json()["id"] == country_id


# Test for fetching a country by name
def test_get_country_by_name():
    country_name = name
    response = requests.get(f"{BASE_URL}/api/v1/countries/name/{country_name}")
    assert response.status_code == 200
    assert response.json()["name"] == country_name


# Test for searching countries by name pattern
@pytest.mark.parametrize(
    "query, expected_status",
    [("Test", 200), ("NonExistent", 200)],
)
def test_search_countries(query, expected_status):
    response = requests.get(f"{BASE_URL}/api/v1/countries/search/?query={query}")
    assert response.status_code == expected_status
    if query == "ab":
        assert len(response.json()) > 0
    else:
        assert len(response.json()) == 0


# Test for fetching all countries
def test_get_all_countries():
    response = requests.get(f"{BASE_URL}/api/v1/countries/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Test for updating a country
def test_modify_country():
    country_id = id
    updated_data = {
            "name": "UpdatedLand",
            "updated_by": 2,
            "active": False
        }
    
    response = requests.put(f"{BASE_URL}/api/v1/countries/{country_id}", json=updated_data)
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedLand"
    assert response.json()["active"] is False


# Test for deleting a country
def test_remove_country():
    country_id = id
    response = requests.delete(f"{BASE_URL}/api/v1/countries/{country_id}")
    assert response.status_code == 200
    assert response.json()["message"] == f"Country with ID {country_id} has been deleted successfully."
