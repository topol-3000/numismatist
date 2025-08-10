"""Tests for grading info endpoints."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


# Helper functions (moved from test_constants.py)
def build_grading_companies_mapping(companies) -> dict[str, str]:
    """Build a mapping of short names to IDs from company objects."""
    return {company.short_name: company.id for company in companies}


def get_sample_grading_full(pcgs_id: str) -> dict:
    return {
        "company_id": pcgs_id,
        "certificate_number": "21690270",
        "grade": "MS 70",
        "grade_details": "CLEANED",
        "note": "Nice coin with original luster",
        "certificate_url": "https://www.pcgs.com/cert/21690270"
    }


def get_sample_grading_minimal(ngc_id: str) -> dict:
    return {
        "company_id": ngc_id,
        "certificate_number": "5712634-007"
    }


def get_sample_grading_update() -> dict:
    return {
        "grade": "MS 70",
        "grade_details": "SCRATCHED",
        "note": "Small scratch on obverse",
        "certificate_number": "5712634-006",
        "certificate_url": "https://www.ngccoin.com/certlookup/5712634-006/69/"
    }


def get_test_item_grading_info(ngc_id: str) -> dict:
    return {
        "certificate_number": "5712634-005",
        "grade": "MS 65",
        "grade_details": "CLEANED",
        "note": "Test coin with original surfaces",
        "company_id": ngc_id
    }


# Test constants
INVALID_COMPANY_ID = str(uuid4())
FAKE_ITEM_ID = str(uuid4())
EXPECTED_MODERN_GRADES = ["MS 70", "PR 70"]
EXPECTED_DETAILS_GRADES = ["CLEANED"]
EXPECTED_PCGS_GRADES = ["PR "]
EXPECTED_NGC_GRADES = ["PF "]


@pytest.fixture
def grading_companies_mapping(test_grading_companies):
    """Build a mapping of company short names to IDs."""
    return build_grading_companies_mapping(test_grading_companies)


@pytest.fixture
def sample_grading_data(grading_companies_mapping):
    return get_sample_grading_full(grading_companies_mapping["PCGS"]).copy()


@pytest.fixture
def minimal_grading_data(grading_companies_mapping):
    return get_sample_grading_minimal(grading_companies_mapping["NGC"]).copy()


@pytest.fixture 
def sample_grading_update():
    return get_sample_grading_update()


@pytest.fixture
def test_item_grading_info_data(grading_companies_mapping):
    """Get expected grading info data for test_item fixture."""
    return {
        "certificate_number": "5712634-005",
        "grade": "MS 65", 
        "grade_details": "CLEANED",
        "note": "Test coin with original surfaces",
        "company_id": grading_companies_mapping["NGC"]
    }


def assert_grading_info_fields(grading_info, expected_data):
    for key, value in expected_data.items():
        assert grading_info[key] == value


class TestGradingInfoAPI:

    def test_get_grading_info_empty(self, authenticated_client: TestClient, test_item_no_grading_info):
        response = authenticated_client.get(f"/api/items/{test_item_no_grading_info.id}/grading-info/")
        assert response.status_code == 200
        assert response.json() is None

    def test_get_grading_info_with_data(self, authenticated_client: TestClient, test_item, test_item_grading_info_data):
        response = authenticated_client.get(f"/api/items/{test_item.id}/grading-info/")
        assert response.status_code == 200
        
        grading_info = response.json()
        assert grading_info is not None
        assert_grading_info_fields(grading_info, test_item_grading_info_data)

    def test_create_grading_info(self, authenticated_client: TestClient, test_item_no_grading_info, sample_grading_data):
        response = authenticated_client.post(
            f"/api/items/{test_item_no_grading_info.id}/grading-info/",
            json=sample_grading_data
        )
        assert response.status_code == 201
        assert_grading_info_fields(response.json(), sample_grading_data)

    def test_create_grading_info_minimal(self, authenticated_client: TestClient, test_item_no_grading_info, minimal_grading_data):
        response = authenticated_client.post(
            f"/api/items/{test_item_no_grading_info.id}/grading-info/",
            json=minimal_grading_data
        )
        assert response.status_code == 201
        
        grading_info = response.json()
        assert grading_info["certificate_number"] == minimal_grading_data["certificate_number"]
        assert grading_info["company_id"] == minimal_grading_data["company_id"]
        assert grading_info["grade"] is None
        assert grading_info["grade_details"] is None
        assert grading_info["note"] is None

    def test_update_grading_info(self, authenticated_client: TestClient, test_item, sample_grading_update, grading_companies_mapping):
        response = authenticated_client.patch(
            f"/api/items/{test_item.id}/grading-info/",
            json=sample_grading_update
        )
        assert response.status_code == 200
        
        updated_info = response.json()
        assert_grading_info_fields(updated_info, sample_grading_update)
        # Note: company_id should remain the same as the original (NGC)
        assert updated_info["company_id"] == grading_companies_mapping["NGC"]

    def test_delete_grading_info(self, authenticated_client: TestClient, test_item):
        response = authenticated_client.delete(f"/api/items/{test_item.id}/grading-info/")
        assert response.status_code == 204

        response = authenticated_client.get(f"/api/items/{test_item.id}/grading-info/")
        assert response.status_code == 200
        assert response.json() is None

    def test_grading_info_with_invalid_company(self, authenticated_client: TestClient, test_item_no_grading_info):
        grading_data = {
            "company_id": INVALID_COMPANY_ID,
            "certificate_number": "21690270",
            "grade": "MS 67"
        }
        
        response = authenticated_client.post(
            f"/api/items/{test_item_no_grading_info.id}/grading-info/",
            json=grading_data
        )
        assert response.status_code in [201, 400, 422]

    def test_grading_info_validation(self, authenticated_client: TestClient, test_item_no_grading_info, grading_companies_mapping):
        grading_data = {
            "company_id": grading_companies_mapping["PCGS"],
            "grade": "MS 67"
        }
        
        response = authenticated_client.post(
            f"/api/items/{test_item_no_grading_info.id}/grading-info/",
            json=grading_data
        )
        assert response.status_code == 422

    def test_grading_info_item_ownership(self, authenticated_client: TestClient, test_item, another_user_client: TestClient):
        response = another_user_client.get(f"/api/items/{test_item.id}/grading-info/")
        assert response.status_code == 404

    def test_grading_info_with_nonexistent_item(self, authenticated_client: TestClient):
        response = authenticated_client.get(f"/api/items/{FAKE_ITEM_ID}/grading-info/")
        assert response.status_code == 404

    def test_item_with_grading_info_in_detail_view(self, authenticated_client: TestClient, test_item, test_item_grading_info_data):
        response = authenticated_client.get(f"/api/items/{test_item.id}")
        assert response.status_code == 200
        
        item_data = response.json()
        assert "grading_info" in item_data
        assert item_data["grading_info"] is not None
        assert_grading_info_fields(item_data["grading_info"], test_item_grading_info_data)

    def test_multiple_grading_info_entries(self, authenticated_client: TestClient, test_item_no_grading_info, grading_companies_mapping):
        grading_data_1 = {
            "company_id": grading_companies_mapping["PCGS"],
            "certificate_number": "21690271",
            "grade": "MS 70"
        }
        
        response = authenticated_client.post(
            f"/api/items/{test_item_no_grading_info.id}/grading-info/",
            json=grading_data_1
        )
        assert response.status_code == 201
        
        grading_data_2 = {
            "company_id": grading_companies_mapping["NGC"],
            "certificate_number": "5712634-008",
            "grade": "MS 70"
        }
        
        response = authenticated_client.post(
            f"/api/items/{test_item_no_grading_info.id}/grading-info/",
            json=grading_data_2
        )
        assert response.status_code == 400
        assert "already has grading info" in response.json()["detail"]


class TestGradingCompanyGrades:

    def test_get_company_grades(self, authenticated_client, grading_companies_mapping):
        response = authenticated_client.get(f"/api/grading-companies/{grading_companies_mapping['PCGS']}/grades")
        assert response.status_code == 200
        
        grades_data = response.json()
        assert isinstance(grades_data, dict)
        assert "modern" in grades_data
        assert "details" in grades_data

        modern_grades = grades_data["modern"]
        assert isinstance(modern_grades, list)
        assert len(modern_grades) > 0
        for grade in EXPECTED_MODERN_GRADES:
            assert grade in modern_grades

        details_grades = grades_data["details"]
        assert isinstance(details_grades, list)
        for grade in EXPECTED_DETAILS_GRADES:
            assert grade in details_grades

    def test_get_company_grades_not_found(self, authenticated_client):
        response = authenticated_client.get(f"/api/grading-companies/{FAKE_ITEM_ID}/grades")
        assert response.status_code == 404
        assert "Grading company not found" in response.json()["detail"]

    def test_different_companies_have_different_grades(self, authenticated_client, grading_companies_mapping):
        pcgs_response = authenticated_client.get(f"/api/grading-companies/{grading_companies_mapping['PCGS']}/grades")
        ngc_response = authenticated_client.get(f"/api/grading-companies/{grading_companies_mapping['NGC']}/grades")
        
        assert pcgs_response.status_code == 200
        assert ngc_response.status_code == 200
        
        pcgs_grades = pcgs_response.json()
        ngc_grades = ngc_response.json()

        pcgs_modern = pcgs_grades["modern"]
        ngc_modern = ngc_grades["modern"]

        assert any(grade_type in grade for grade in pcgs_modern for grade_type in EXPECTED_PCGS_GRADES)
        assert any(grade_type in grade for grade in ngc_modern for grade_type in EXPECTED_NGC_GRADES)
