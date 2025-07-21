#!/usr/bin/env python3
"""Unit and integration tests for the GithubOrgClient class."""

import unittest
from typing import Dict, List
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
import fixtures


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient class methods."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str,
                 mock_get_json: unittest.mock.Mock) -> None:
        """Test that GithubOrgClient.org returns correct org data."""
        expected = {"login": org_name}
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        org = client.org

        self.assertEqual(org, expected)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url retrieves repos_url from self.org."""
        client = GithubOrgClient("test_org")
        payload = {"repos_url": "https://api.github.com/orgs/test_org/repos"}

        with patch.object(GithubOrgClient, "org",
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = payload
            url = client._public_repos_url
            self.assertEqual(url, payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: unittest.mock.Mock) -> None:
        """
        Test that public_repos returns all repository names
        when no license is specified.
        """
        repos = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
        ]
        mock_get_json.return_value = repos

        client = GithubOrgClient("org")
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "url"
            result = client.public_repos()
            self.assertEqual(result, ["repo1", "repo2"])
            mock_get_json.assert_called_once_with("url")

    @patch("client.get_json")
    def test_public_repos_with_license(
        self, mock_get_json: unittest.mock.Mock
    ) -> None:
        """Test that public_repos filters only Apache-2.0 licensed repos."""
        mock_get_json.return_value = fixtures.repos_payload

        client = GithubOrgClient("org")
        with patch.object(
            GithubOrgClient, "_public_repos_url", new_callable=PropertyMock
        ) as mock_url:
            mock_url.return_value = "url"
            result = client.public_repos(license="apache-2.0")
            self.assertEqual(result, fixtures.apache2_repos)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other"}}, "my_license", False),
        ({}, "any", False)
    ])
    def test_has_license(
        self, repo: Dict, license_key: str, expected: bool
    ) -> None:
        """Test has_license correctly checks repo license key."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient's public_repos method."""

    @classmethod
    def setUpClass(cls) -> None:
        """Patch requests.get to return predefined org and repo payloads."""
        cls.get_patcher = patch("client.requests.get")
        mock_get = cls.get_patcher.start()

        def json_side_effect(url: str) -> unittest.mock.Mock:
            if "orgs" in url:
                return unittest.mock.Mock(json=lambda: cls.org_payload)
            return unittest.mock.Mock(json=lambda: cls.repos_payload)

        mock_get.side_effect = json_side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """Stop patching requests.get after tests."""
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """Test public_repos returns all repos for the given org."""
        client = GithubOrgClient("org_name")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """Test public_repos returns only repos with Apache 2.0 license."""
        client = GithubOrgClient("org_name")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.apache2_repos)


if __name__ == "__main__":
    unittest.main()
