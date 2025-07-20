#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient."""

import unittest
from typing import Dict
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
import fixtures  # Assumed to be available


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient class."""

    @parameterized.expand([("google",), ("abc",)])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that org method returns expected result."""
        # Setup mock to return a fake dict
        mock_get_json.return_value = {"login": org_name}

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}")
        self.assertEqual(result, {"login": org_name})

    def test_public_repos_url(self) -> None:
        """
        Test that _public_repos_url returns the expected URL from
        the mocked org property.
        """
        payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        client = GithubOrgClient("google")

        with patch.object(
            GithubOrgClient, "org",
            new_callable=PropertyMock, return_value=payload
        ):
            self.assertEqual(client._public_repos_url, payload["repos_url"])

    @patch("client.get_json", autospec=True)
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Test public_repos returns expected repo names list, and mocks
        _public_repos_url and get_json properly.
        """
        repos_payload = [
            {"name": "repo1"},
            {"name": "repo2"},
            {"name": "repo3"},
        ]
        mock_get_json.return_value = repos_payload
        client = GithubOrgClient("google")

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value="https://api.github.com/orgs/google/repos",
        ) as mock_public_url:
            repos = client.public_repos()

            self.assertEqual(repos, ["repo1", "repo2", "repo3"])
            mock_public_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                "https://api.github.com/orgs/google/repos"
            )

    @parameterized.expand(
        [
            ({"license": {"key": "my_license"}}, "my_license", True),
            ({"license": {"key": "other_license"}}, "my_license", False),
        ]
    )
    def test_has_license(self, repo: Dict,
                         license_key: str, expected: bool) -> None:
        """
        Test has_license returns correct boolean depending on if
        license_key matches the repo's license key.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.has_license(repo, license_key), expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    [
        (
            fixtures.org_payload,
            fixtures.repos_payload,
            fixtures.expected_repos,
            fixtures.apache2_repos,
        )
    ],
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient.public_repos using fixtures."""

    @classmethod
    def setUpClass(cls) -> None:
        """
        Setup patchers for requests.get to return appropriate payloads
        for org and repos URLs.
        """
        cls.get_patcher = patch("requests.get", autospec=True)
        mock_get = cls.get_patcher.start()

        def side_effect(url: str, *args, **kwargs) -> Mock:
            mock_resp = Mock()
            if url == cls.org_payload["url"]:
                mock_resp.json.return_value = cls.org_payload["payload"]
            elif url == cls.repos_payload["url"]:
                mock_resp.json.return_value = cls.repos_payload["payload"]
            else:
                mock_resp.json.return_value = None
            return mock_resp

        # Add 'url' keys to fixture dictionaries for URL matching

        cls.org_payload["url"] = (
            f"https://api.github.com/orgs/"
            f"{cls.org_payload['payload']['login']}"
        )

        cls.repos_payload["url"] = cls.org_payload["payload"]["repos_url"]

        mock_get.side_effect = side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop the patcher for requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Test that public_repos returns expected list of repo names based
        on integration fixtures.
        """
        client = GithubOrgClient(self.org_payload["payload"]["login"])
        self.assertEqual(client.public_repos(), self.expected_repos)
