#!/usr/bin/env python3
"""Test for GithubOrgClient."""

import unittest
from unittest.mock import patch
from parameterized import parameterized
from client import GithubOrgClient


class TestGithubOrgClient(unittest.TestCase):
    """Test the GithubOrgClient class."""

    @patch('client.get_json')
    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    def test_org(self, mock_get_json, org_name):
        """Test GithubOrgClient.org returns expected value."""
        expected = {"login": org_name}
        mock_get_json.return_value = expected

        client = GithubOrgClient(org_name)
        result = client.org

        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )
        self.assertEqual(result, expected)
