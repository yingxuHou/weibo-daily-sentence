from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlencode, urlparse
import mimetypes

import requests
from loguru import logger

from app.core.config import settings


class WeiboConfigurationError(RuntimeError):
    """Raised when required Weibo credentials are missing."""


class WeiboAPIError(RuntimeError):
    """Raised when the Weibo API rejects or cannot complete a request."""

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[int] = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.error_code = error_code
        self.retryable = retryable


@dataclass(frozen=True)
class WeiboPublishResult:
    weibo_id: str
    raw: Dict[str, Any]


class WeiboPublisher:
    """Small Weibo OAuth2 and status publishing client."""

    API_BASE = "https://api.weibo.com/2"
    AUTHORIZE_URL = "https://api.weibo.com/oauth2/authorize"
    ACCESS_TOKEN_URL = "https://api.weibo.com/oauth2/access_token"

    def __init__(
        self,
        *,
        app_key: Optional[str] = None,
        app_secret: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        access_token: Optional[str] = None,
        session: Optional[requests.Session] = None,
        timeout: Optional[float] = None,
        max_image_bytes: Optional[int] = None,
    ):
        self.app_key = app_key if app_key is not None else settings.WEIBO_APP_KEY
        self.app_secret = (
            app_secret if app_secret is not None else settings.WEIBO_APP_SECRET
        )
        self.redirect_uri = (
            redirect_uri if redirect_uri is not None else settings.WEIBO_REDIRECT_URI
        )
        self.access_token = (
            access_token if access_token is not None else settings.WEIBO_ACCESS_TOKEN
        )
        self.session = session or requests.Session()
        self.timeout = timeout or settings.WEIBO_REQUEST_TIMEOUT_SECONDS
        self.max_image_bytes = max_image_bytes or (
            settings.WEIBO_MAX_IMAGE_SIZE_MB * 1024 * 1024
        )

    @property
    def is_configured(self) -> bool:
        return bool(
            self.app_key
            and self.app_secret
            and self.redirect_uri
            and self.access_token
        )

    def get_authorize_url(self, state: Optional[str] = None) -> str:
        self._require_oauth_config()
        params = {
            "client_id": self.app_key,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        if state:
            params["state"] = state
        return f"{self.AUTHORIZE_URL}?{urlencode(params)}"

    def exchange_code(self, code: str) -> Dict[str, Any]:
        self._require_oauth_config()
        try:
            response = self.session.post(
                self.ACCESS_TOKEN_URL,
                data={
                    "client_id": self.app_key,
                    "client_secret": self.app_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise WeiboAPIError(f"Weibo OAuth request failed: {exc}") from exc
        return self._parse_response(response, "exchange OAuth code")

    def publish(
        self,
        text: str,
        image_source: Optional[str] = None,
    ) -> WeiboPublishResult:
        self._require_publish_config()
        status = text.strip()
        if not status:
            raise ValueError("Weibo status text cannot be empty")

        data = {"access_token": self.access_token, "status": status}
        try:
            if image_source:
                filename, content_type, image_bytes = self._read_image(image_source)
                response = self.session.post(
                    f"{self.API_BASE}/statuses/upload.json",
                    data=data,
                    files={"pic": (filename, image_bytes, content_type)},
                    timeout=self.timeout,
                )
            else:
                response = self.session.post(
                    f"{self.API_BASE}/statuses/update.json",
                    data=data,
                    timeout=self.timeout,
                )
        except requests.RequestException as exc:
            # A POST may have reached Weibo before the connection failed. Blindly
            # retrying can create duplicate posts, so ambiguous network errors are
            # intentionally not marked retryable.
            raise WeiboAPIError(f"Weibo request failed: {exc}") from exc

        payload = self._parse_response(response, "publish status")
        weibo_id = payload.get("idstr") or payload.get("id")
        if not weibo_id:
            raise WeiboAPIError("Weibo response did not include a status id")

        logger.info("Published Weibo status {}", weibo_id)
        return WeiboPublishResult(weibo_id=str(weibo_id), raw=payload)

    def delete(self, weibo_id: str) -> bool:
        self._require_publish_config()
        response = self.session.post(
            f"{self.API_BASE}/statuses/destroy.json",
            data={"access_token": self.access_token, "id": weibo_id},
            timeout=self.timeout,
        )
        self._parse_response(response, "delete status")
        return True

    def _read_image(self, source: str) -> Tuple[str, str, bytes]:
        parsed = urlparse(source)
        if parsed.scheme in ("http", "https"):
            return self._download_image(source)
        is_windows_path = (
            len(parsed.scheme) == 1
            and len(source) > 2
            and source[1] == ":"
            and source[2] in ("\\", "/")
        )
        if parsed.scheme and not is_windows_path:
            raise WeiboAPIError(f"Unsupported image URL scheme: {parsed.scheme}")

        path = Path(source)
        if not path.is_file():
            raise WeiboAPIError(f"Image file does not exist: {source}")
        if path.stat().st_size > self.max_image_bytes:
            raise WeiboAPIError("Image exceeds configured size limit")

        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return path.name, content_type, path.read_bytes()

    def _download_image(self, url: str) -> Tuple[str, str, bytes]:
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise WeiboAPIError(f"Failed to download publish image: {exc}") from exc

        content_type = response.headers.get("Content-Type", "").split(";")[0]
        if not content_type.startswith("image/"):
            raise WeiboAPIError(
                f"Remote image returned unsupported content type: {content_type or 'unknown'}"
            )
        if len(response.content) > self.max_image_bytes:
            raise WeiboAPIError("Image exceeds configured size limit")

        filename = Path(urlparse(url).path).name or "weibo-image"
        extension = mimetypes.guess_extension(content_type)
        if extension and not Path(filename).suffix:
            filename += extension
        return filename, content_type, response.content

    def _parse_response(
        self,
        response: requests.Response,
        action: str,
    ) -> Dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise WeiboAPIError(
                f"Weibo returned a non-JSON response while trying to {action}"
            ) from exc

        if response.ok and "error_code" not in payload:
            return payload

        error_code = payload.get("error_code")
        message = payload.get("error") or f"HTTP {response.status_code}"
        retryable = response.status_code == 429 or response.status_code >= 500
        raise WeiboAPIError(
            f"Weibo could not {action}: {message}",
            error_code=error_code,
            retryable=retryable,
        )

    def _require_oauth_config(self) -> None:
        missing = [
            name
            for name, value in (
                ("WEIBO_APP_KEY", self.app_key),
                ("WEIBO_APP_SECRET", self.app_secret),
                ("WEIBO_REDIRECT_URI", self.redirect_uri),
            )
            if not value
        ]
        if missing:
            raise WeiboConfigurationError(
                f"Missing Weibo configuration: {', '.join(missing)}"
            )

    def _require_publish_config(self) -> None:
        self._require_oauth_config()
        if not self.access_token:
            raise WeiboConfigurationError(
                "Missing Weibo configuration: WEIBO_ACCESS_TOKEN"
            )
