"""POST /pet/{petId} form-data update tests — Petstore Swagger v2."""

import logging

import pytest

from src.api.client import PetstoreApiClient

logger = logging.getLogger(__name__)

pytestmark = pytest.mark.api


@pytest.mark.smoke
def test_update_name_only_returns_200(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    new_name = "UpdatedNameOnly"

    response = api_client.update_pet_with_form(pet_id, name=new_name)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Body: {response.text[:300]}"

    pet = api_client.get_pet_by_id(pet_id).json()
    assert pet["name"] == new_name


@pytest.mark.smoke
def test_update_status_only_returns_200(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    new_status = "sold"

    response = api_client.update_pet_with_form(pet_id, status=new_status)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Body: {response.text[:300]}"
    assert api_client.get_pet_by_id(pet_id).json()["status"] == new_status


@pytest.mark.smoke
def test_update_name_and_status_returns_200(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    new_name = "BothFieldsUpdated"
    new_status = "pending"

    response = api_client.update_pet_with_form(pet_id, name=new_name, status=new_status)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Body: {response.text[:300]}"

    pet = api_client.get_pet_by_id(pet_id).json()
    assert pet["name"] == new_name
    assert pet["status"] == new_status


def test_update_with_empty_form_data(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    original_name = created_pet["name"]

    response = api_client.update_pet_with_form(pet_id)

    # Petstore demo accepts empty body without error
    assert response.status_code == 200, f"Got {response.status_code}: {response.text[:200]}"

    pet = api_client.get_pet_by_id(pet_id).json()
    assert pet["name"] == original_name, "Empty body must not overwrite the pet name"


@pytest.mark.parametrize("status_value", ["available", "pending", "sold"])
def test_update_status_all_valid_enum_values(
    api_client: PetstoreApiClient, created_pet: dict, status_value: str
):
    pet_id = created_pet["id"]
    response = api_client.update_pet_with_form(pet_id, status=status_value)

    assert response.status_code == 200, f"status='{status_value}' → {response.status_code}"
    assert api_client.get_pet_by_id(pet_id).json()["status"] == status_value
