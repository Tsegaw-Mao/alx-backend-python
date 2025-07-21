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


if __name__ == "__main__":
    unittest.main()
