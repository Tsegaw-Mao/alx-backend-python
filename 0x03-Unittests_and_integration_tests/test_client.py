#!/usr/bin/env python3
"""Unit test for GithubOrgClient.org using patch and parameterized."""

import unittest
from typing import Dict
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit tests for GithubOrgClient class.

    Specifically tests the org property which fetches
    organization data from the GitHub API using get_json.
    """

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name: str,
                 mock_get_json: unittest.mock.Mock) -> None:
        """
        Test that GithubOrgClient.org returns expected
        payload and get_json is called with correct URL.
        """
        expected_payload: Dict = {"login": org_name}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self) -> None:
        """
        Test that GithubOrgClient._public_repos_url returns the
        correct 'repos_url' from the org property.
        """
        fake_repos_url = "https://api.github.com/orgs/test-org/repos"
        fake_org_payload = {"repos_url": fake_repos_url}

        client = GithubOrgClient("test-org")

        with patch.object(
            type(client),
            "org",
            new_callable=unittest.mock.PropertyMock,
            return_value=fake_org_payload
        ):
            result = client._public_repos_url

        self.assertEqual(result, fake_repos_url)


if __name__ == "__main__":
    unittest.main()
