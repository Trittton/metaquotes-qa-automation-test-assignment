import logging
import os
from typing import Any

import requests

from src.api.models import PetPayload

logger = logging.getLogger(__name__)

BASE_URL = os.getenv("PETSTORE_BASE_URL", "https://petstore.swagger.io/v2")
DEFAULT_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))


class PetstoreApiClient:
    """Thin wrapper over requests.Session for Petstore v2."""

    def __init__(self, base_url: str = BASE_URL, timeout: int = DEFAULT_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def create_pet(self, payload: PetPayload) -> requests.Response:
        url = f"{self.base_url}/pet"
        logger.debug("POST %s body=%s", url, payload.as_dict())
        response = self.session.post(url, json=payload.as_dict(), timeout=self.timeout)
        logger.debug("Response %d: %s", response.status_code, response.text[:300])
        return response

    def update_pet_with_form(
        self,
        pet_id: Any,
        name: str | None = None,
        status: str | None = None,
    ) -> requests.Response:
        """POST /pet/{petId} with form data. pet_id is Any to allow negative-test path segments."""
        url = f"{self.base_url}/pet/{pet_id}"
        form_data: dict[str, str] = {}
        if name is not None:
            form_data["name"] = name
        if status is not None:
            form_data["status"] = status

        logger.debug("POST %s form=%s", url, form_data)
        response = self.session.post(url, data=form_data, timeout=self.timeout)
        logger.debug("Response %d: %s", response.status_code, response.text[:300])
        return response

    def get_pet_by_id(self, pet_id: int) -> requests.Response:
        url = f"{self.base_url}/pet/{pet_id}"
        return self.session.get(url, timeout=self.timeout)

    def delete_pet(self, pet_id: int) -> requests.Response:
        url = f"{self.base_url}/pet/{pet_id}"
        return self.session.delete(url, timeout=self.timeout)

    def close(self) -> None:
        self.session.close()
