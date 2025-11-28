"""Tests for OAuth helper functions."""

from unittest.mock import MagicMock, patch

import pytest

from ebay_rest import oauth


@patch("requests.post")
def test_exchange_authorization_code(mock_post: MagicMock):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "abc", "refresh_token": "def"}
    mock_post.return_value.raise_for_status.return_value = None

    data = oauth.exchange_authorization_code(
        client_id="id",
        client_secret="secret",
        code="auth_code",
        redirect_uri="https://example.com/callback",
    )

    assert data["access_token"] == "abc"
    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert "authorization_code" in kwargs["data"]["grant_type"]


@patch("requests.post")
def test_refresh_user_token(mock_post: MagicMock):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"access_token": "new"}
    mock_post.return_value.raise_for_status.return_value = None

    data = oauth.refresh_user_token(
        client_id="id",
        client_secret="secret",
        refresh_token="refresh",
        scopes=["scope1", "scope2"],
    )

    assert data["access_token"] == "new"
    _, kwargs = mock_post.call_args
    assert kwargs["data"]["refresh_token"] == "refresh"
    assert kwargs["data"]["scope"] == "scope1 scope2"


def test_build_authorization_url():
    url = oauth.build_authorization_url(
        client_id="id",
        redirect_uri="https://example.com/callback",
        scopes=["a", "b"],
        state="xyz",
    )
    assert "client_id=id" in url
    assert "scope=a+b" in url
    assert "state=xyz" in url

