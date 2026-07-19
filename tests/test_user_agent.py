"""
Tests for configurable User-Agent functionality.
"""

from unittest.mock import Mock, patch

from wikipedia_mcp import __version__
from wikipedia_mcp.wikipedia_client import WikipediaClient
from wikipedia_mcp.server import create_server


class TestDefaultUserAgent:
    """The default User-Agent identifies this fork, not upstream."""

    def test_default_user_agent_when_none_provided(self):
        client = WikipediaClient()
        assert client.user_agent == WikipediaClient.DEFAULT_USER_AGENT
        assert "apocryphalword/wikipedia-mcp" in client.user_agent
        assert __version__ in client.user_agent
        # Must not carry the upstream shared identifier.
        assert "rudra-ravi" not in client.user_agent

    def test_default_user_agent_in_request_headers(self):
        client = WikipediaClient()
        headers = client._get_request_headers()
        assert headers["User-Agent"] == WikipediaClient.DEFAULT_USER_AGENT


class TestCustomUserAgent:
    """A custom User-Agent overrides the default across all consumers."""

    def test_custom_user_agent_via_constructor(self):
        ua = "MyDeployment/1.0 (https://example.com/contact)"
        client = WikipediaClient(user_agent=ua)
        assert client.user_agent == ua
        assert client._get_request_headers()["User-Agent"] == ua

    def test_empty_user_agent_falls_back_to_default(self):
        assert WikipediaClient(user_agent="").user_agent == WikipediaClient.DEFAULT_USER_AGENT

    def test_whitespace_user_agent_falls_back_to_default(self):
        assert WikipediaClient(user_agent="   ").user_agent == WikipediaClient.DEFAULT_USER_AGENT

    def test_user_agent_is_trimmed(self):
        client = WikipediaClient(user_agent="  Trimmed/1.0  ")
        assert client.user_agent == "Trimmed/1.0"

    @patch("wikipedia_mcp.wikipedia_client.requests.get")
    def test_custom_user_agent_sent_on_requests(self, mock_get):
        ua = "MyDeployment/1.0 (https://example.com/contact)"
        client = WikipediaClient(user_agent=ua)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"query": {"search": []}}
        mock_get.return_value = mock_response

        client.search("Python")

        _, kwargs = mock_get.call_args
        assert kwargs["headers"]["User-Agent"] == ua


class TestCreateServerThreadsUserAgent:
    """create_server passes the User-Agent through to the client."""

    def test_create_server_threads_user_agent(self):
        ua = "ServerLevel/2.0 (https://example.com)"
        with patch("wikipedia_mcp.server.WikipediaClient") as mock_client:
            create_server(user_agent=ua)
        _, kwargs = mock_client.call_args
        assert kwargs["user_agent"] == ua
