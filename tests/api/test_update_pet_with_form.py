"""POST /pet/{petId} form-data update tests — Petstore Swagger v2."""

import json
import jsonschema
import pytest

from src.api.client import PetstoreApiClient

pytestmark = pytest.mark.api

_API_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["code", "type", "message"],
    "properties": {
        "code": {"type": "integer"},
        "type": {"type": "string"},
        "message": {"type": "string"},
    },
}


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


def test_update_name_with_very_long_string(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    long_name = "A" * 10_000

    response = api_client.update_pet_with_form(pet_id, name=long_name)

    assert response.status_code != 500, "Server must not crash on a long name"
    assert response.status_code in (200, 400, 413), f"Unexpected {response.status_code}"

    if response.status_code == 200:
        stored = api_client.get_pet_by_id(pet_id).json().get("name", "")
        assert stored == long_name, (
            f"Silent truncation: sent {len(long_name)} chars, stored {len(stored)}"
        )


@pytest.mark.parametrize(
    "special_name",
    [
        "Ünïcödé Pét",
        "<script>alert(1)</script>",
        "'; DROP TABLE pets; --",
        "🐕 Dog 🐾",
        "name\x00with\x00nulls",
    ],
)
def test_update_name_with_special_characters(
    api_client: PetstoreApiClient, created_pet: dict, special_name: str
):
    pet_id = created_pet["id"]
    response = api_client.update_pet_with_form(pet_id, name=special_name)

    assert response.status_code != 500, f"Server returned 500 for name={special_name!r}"

    if response.status_code == 200:
        get_resp = api_client.get_pet_by_id(pet_id)
        if get_resp.status_code == 200:
            stored = get_resp.json().get("name")
            assert stored is not None, f"Stored null for name={special_name!r}"


@pytest.mark.negative
def test_update_with_alphabetic_pet_id_returns_error(api_client: PetstoreApiClient):
    response = api_client.update_pet_with_form("abc", name="ShouldFail")

    assert response.status_code >= 400, (
        f"Expected 4xx for alphabetic petId, got {response.status_code}. Body: {response.text[:300]}"
    )


@pytest.mark.negative
@pytest.mark.xfail(strict=False, reason="BUG: server accepts petId=0, spec expects 405")
def test_update_with_zero_pet_id(api_client: PetstoreApiClient):
    response = api_client.update_pet_with_form(0, name="ZeroIdTest")
    assert response.status_code == 405, f"Expected 405 for petId=0, got {response.status_code}"


@pytest.mark.negative
@pytest.mark.xfail(strict=False, reason="BUG: server accepts negative petId, spec expects 405")
def test_update_with_negative_pet_id(api_client: PetstoreApiClient):
    response = api_client.update_pet_with_form(-1, name="NegativeIdTest")
    assert response.status_code == 405, f"Expected 405 for petId=-1, got {response.status_code}"


@pytest.mark.negative
@pytest.mark.xfail(strict=False, reason="BUG: server accepts updates for non-existent IDs, spec expects 404/405")
def test_update_nonexistent_pet_id(api_client: PetstoreApiClient):
    response = api_client.update_pet_with_form(9_999_999_987_654_321, name="GhostPet")

    assert response.status_code in (404, 405), (
        f"Expected 404 or 405 for non-existent petId, got {response.status_code}"
    )

def test_wrong_content_type_sends_json_body(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    url = f"{api_client.base_url}/pet/{pet_id}"
    body = json.dumps({"name": "JsonBodyTest"})

    response = api_client.session.post(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=api_client.timeout,
    )

    assert response.status_code != 500, "Server must not crash on JSON body"

@pytest.mark.smoke
def test_successful_update_response_schema(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    response = api_client.update_pet_with_form(pet_id, name="SchemaTest", status="available")

    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Body: {response.text[:300]}"

    body = response.json()
    jsonschema.validate(instance=body, schema=_API_RESPONSE_SCHEMA)
    assert body["code"] == 200


def test_update_is_applied_to_correct_pet(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]
    new_name = "ConsistencyCheck"

    response = api_client.update_pet_with_form(pet_id, name=new_name)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    pet = api_client.get_pet_by_id(pet_id).json()
    assert pet.get("id") == pet_id
    assert pet.get("name") == new_name, f"Expected {new_name!r}, got {pet.get('name')!r}"

@pytest.mark.negative
@pytest.mark.xfail(
    strict=True,
    reason="BUG: server accepts invalid status 'flying' instead of returning 405",
)
def test_update_with_invalid_status_value(api_client: PetstoreApiClient, created_pet: dict):
    pet_id = created_pet["id"]

    response = api_client.update_pet_with_form(pet_id, status="flying")

    if response.status_code == 200:
        stored_status = api_client.get_pet_by_id(pet_id).json().get("status")
        assert stored_status in ("available", "pending", "sold"), (
            f"Server stored invalid status '{stored_status}'"
        )
    else:
        assert response.status_code in (400, 405)
