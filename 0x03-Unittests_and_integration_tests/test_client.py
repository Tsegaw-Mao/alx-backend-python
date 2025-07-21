#!/usr/bin/env python3
"""Unit test for GithubOrgClient.org using patch and parameterized."""

import unittest
from typing import Dict
from unittest.mock import patch, PropertyMock
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

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json: unittest.mock.Mock) -> None:
        """
        Test GithubOrgClient.public_repos returns the expected list of
        repository names based on a mocked payload.

        Args:
            mock_get_json (Mock): Mocked get_json function.
        """
        # Mocked repos payload returned by get_json
        mocked_repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None},
        ]
        mock_get_json.return_value = mocked_repos_payload

        fake_repos_url = "https://api.github.com/orgs/test-org/repos"

        client = GithubOrgClient("test-org")

        with patch.object(
            type(client),
            "_public_repos_url",
            new_callable=PropertyMock,
            return_value=fake_repos_url
        ) as mock_public_repos_url:
            repos = client.public_repos()

        # Assert the returned repo names match those in mocked payload
        expected_repo_names = ["repo1", "repo2", "repo3"]
        assert repos == expected_repo_names

        # Ensure _public_repos_url property was called once
        mock_public_repos_url.assert_called_once()

        # Ensure get_json was called once with the fake repos URL
        mock_get_json.assert_called_once_with(fake_repos_url)

        @parameterized.expand([
            (
                {"license": {"key": "my_license"}},  # repo
                "my_license",                        # license_key
                True                                 # expected
            ),
            (
                {"license": {"key": "other_license"}},
                "my_license",
                False
            ),
        ])
        def test_has_license(
            self, repo: dict, license_key: str, expected: bool
        ) -> None:
            """
            Test GithubOrgClient.has_license returns True if the repo has the
            given license key, otherwise False.

            Args:
                repo (dict): The repository metadata.
                license_key (str): The license key to check for.
                expected (bool): The expected result.
            """
            result = GithubOrgClient.has_license(repo, license_key)
            self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
