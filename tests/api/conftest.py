import uuid

import pytest

from src.api.client import PetstoreApiClient
from src.api.models import PetPayload


@pytest.fixture(scope="session")
def api_client():
    client = PetstoreApiClient()
    yield client
    client.close()


@pytest.fixture()
def created_pet(api_client: PetstoreApiClient) -> dict:
    """Creates a pet before each test and deletes it after (best-effort on the demo server)."""
    payload = PetPayload(name=f"TestPet_{uuid.uuid4().hex[:12]}", status="available")
    response = api_client.create_pet(payload)
    assert response.status_code == 200, (
        f"Precondition failed: could not create pet. "
        f"Status={response.status_code}, Body={response.text[:200]}"
    )
    pet_data = response.json()

    yield pet_data

    api_client.delete_pet(pet_data["id"])
