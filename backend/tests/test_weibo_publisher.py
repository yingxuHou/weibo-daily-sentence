import os
from pathlib import Path

import pytest

os.environ["DEBUG"] = "False"

from app.publishers.weibo import WeiboAPIError, WeiboPublisher


class FakeResponse:
    def __init__(
        self,
        payload,
        *,
        status_code=200,
        content=b"",
        headers=None,
    ):
        self.payload = payload
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}
        self.ok = 200 <= status_code < 300

    def json(self):
        return self.payload

    def raise_for_status(self):
        if not self.ok:
            raise RuntimeError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, post_response, get_response=None):
        self.post_response = post_response
        self.get_response = get_response
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_calls.append((url, kwargs))
        return self.post_response

    def get(self, url, **kwargs):
        self.get_calls.append((url, kwargs))
        return self.get_response


def make_publisher(session):
    return WeiboPublisher(
        app_key="key",
        app_secret="secret",
        redirect_uri="https://example.com/callback",
        access_token="token",
        session=session,
    )


def test_publish_text_status_uses_update_endpoint():
    session = FakeSession(FakeResponse({"idstr": "123"}))

    result = make_publisher(session).publish("hello")

    assert result.weibo_id == "123"
    assert session.post_calls[0][0].endswith("/statuses/update.json")
    assert session.post_calls[0][1]["data"]["status"] == "hello"


def test_publish_local_image_uses_upload_endpoint(tmp_path: Path):
    image = tmp_path / "post.png"
    image.write_bytes(b"png-data")
    session = FakeSession(FakeResponse({"id": 456}))

    result = make_publisher(session).publish("with image", str(image))

    assert result.weibo_id == "456"
    url, kwargs = session.post_calls[0]
    assert url.endswith("/statuses/upload.json")
    assert kwargs["files"]["pic"][0] == "post.png"
    assert kwargs["files"]["pic"][1] == b"png-data"


def test_publish_remote_image_downloads_before_upload():
    session = FakeSession(
        FakeResponse({"idstr": "789"}),
        FakeResponse(
            {},
            content=b"image-data",
            headers={"Content-Type": "image/jpeg"},
        ),
    )

    result = make_publisher(session).publish(
        "remote image",
        "https://cdn.example.com/post.jpg",
    )

    assert result.weibo_id == "789"
    assert session.get_calls[0][0] == "https://cdn.example.com/post.jpg"
    assert session.post_calls[0][1]["files"]["pic"][1] == b"image-data"


def test_api_error_keeps_error_code_and_retry_hint():
    session = FakeSession(
        FakeResponse(
            {"error": "rate limit", "error_code": 10023},
            status_code=429,
        )
    )

    with pytest.raises(WeiboAPIError) as error:
        make_publisher(session).publish("hello")

    assert error.value.error_code == 10023
    assert error.value.retryable is True


def test_authorize_url_is_encoded():
    publisher = make_publisher(FakeSession(FakeResponse({})))

    url = publisher.get_authorize_url("csrf value")

    assert "state=csrf+value" in url
    assert "redirect_uri=https%3A%2F%2Fexample.com%2Fcallback" in url
