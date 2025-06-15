"""entegra Authentication."""

from __future__ import annotations

import typing as t
from datetime import datetime, timedelta

import requests
from singer_sdk.authenticators import SimpleAuthenticator
from singer_sdk.helpers._util import utc_now

if t.TYPE_CHECKING:
    from singer_sdk.streams import RESTStream


class EntegraAuthenticator(SimpleAuthenticator):
    """Authenticator class for entegra using JWT tokens."""

    def __init__(
        self,
        stream: RESTStream,
        auth_endpoint: str | None = None,
    ) -> None:
        """Initialize the authenticator.

        Args:
            stream: The stream instance to use with this authenticator.
            auth_endpoint: The endpoint to authenticate against.
        """
        super().__init__(stream=stream)
        self._auth_endpoint = auth_endpoint or f"{stream.url_base}/api/user/token/obtain/"
        self._stream = stream
        self._token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: datetime | None = None

    @classmethod
    def create_for_stream(
        cls,
        stream: RESTStream,  # noqa: ANN401
    ) -> EntegraAuthenticator:
        """Instantiate an authenticator for a specific Singer stream.

        Args:
            stream: The Singer stream instance.

        Returns:
            A new authenticator.
        """
        return cls(stream=stream)

    def is_token_valid(self) -> bool:
        """Check if current token is valid.

        Returns:
            True if token exists and is not expired.
        """
        return (
            self._token is not None
            and self._expires_at is not None
            and utc_now() < self._expires_at
        )

    def update_access_token(self) -> None:
        """Update the access token."""
        if self.is_token_valid():
            return

        auth_request_payload = {
            "email": self._stream.config["email"],
            "password": self._stream.config["password"],
        }

        response = requests.post(
            self._auth_endpoint,
            json=auth_request_payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
            verify=False,  # For testing only - in production, fix SSL certificates
        )
        response.raise_for_status()

        auth_response = response.json()
        self._token = auth_response["access"]
        self._refresh_token = auth_response.get("refresh")
        
        # JWT tokens typically expire after 90 days according to the API docs,
        # but we'll refresh more frequently to be safe
        self._expires_at = utc_now() + timedelta(hours=1)

    @property
    def auth_header(self) -> dict[str, str]:
        """Return the authorization header.

        Returns:
            The authorization header for requests.
        """
        if not self.is_token_valid():
            self.update_access_token()
        return {"Authorization": f"JWT {self._token}"}

    def __call__(self, request: requests.PreparedRequest) -> requests.PreparedRequest:
        """Apply authentication to the request.

        Args:
            request: The request to authenticate.

        Returns:
            The authenticated request.
        """
        if not self.is_token_valid():
            self.update_access_token()
        
        request.headers["Authorization"] = f"JWT {self._token}"
        return request
