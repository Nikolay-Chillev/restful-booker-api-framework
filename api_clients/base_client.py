import time
from typing import Any, Optional

import allure
import requests

from config.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseClient:
    """Base HTTP client with logging, session management, and response tracking."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.BASE_URL
        self.timeout = settings.REQUEST_TIMEOUT
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
        json_data: Optional[Any] = None,
    ) -> requests.Response:
        """Send an HTTP request with logging and timing."""
        url = f"{self.base_url}{endpoint}"

        logger.info(f"{method.upper()} {url}")
        if json_data:
            logger.debug(f"Request body: {json_data}")

        start_time = time.time()
        response = self.session.request(
            method=method,
            url=url,
            headers={**self.session.headers, **(headers or {})},
            params=params,
            json=json_data,
            timeout=self.timeout,
        )
        elapsed = time.time() - start_time

        logger.info(f"Response: {response.status_code} ({elapsed:.2f}s)")
        if response.text:
            logger.debug(f"Response body: {response.text[:500]}")

        self._attach_to_allure(method, url, json_data, response, elapsed)

        return response

    def _attach_to_allure(
        self,
        method: str,
        url: str,
        request_body: Any,
        response: requests.Response,
        elapsed: float,
    ) -> None:
        """Attach request/response details to Allure report."""
        request_info = f"{method.upper()} {url}\nTime: {elapsed:.2f}s"
        if request_body:
            request_info += f"\nBody: {request_body}"
        allure.attach(request_info, name="Request", attachment_type=allure.attachment_type.TEXT)

        response_info = f"Status: {response.status_code}\nBody: {response.text[:1000]}"
        allure.attach(response_info, name="Response", attachment_type=allure.attachment_type.TEXT)

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request("DELETE", endpoint, **kwargs)

    def close(self) -> None:
        """Close the underlying session."""
        self.session.close()
