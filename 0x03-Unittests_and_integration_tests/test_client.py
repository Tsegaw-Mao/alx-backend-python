#!/usr/bin/env python3
"""Tests for client GithubOrgClient public_repos methods."""

import unittest
from unittest.mock import patch, PropertyMock
from client import GithubOrgClient
from fixtures import repos_payload, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Test GithubOrgClient public_repos related methods."""

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected repo names list."""
        mock_get_json.return_value = repos_payload

        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = (
                'https://api.github.com/orgs/google/repos'
            )

            client = GithubOrgClient('google')
            repos = client.public_repos()

            expected_repos = [repo['name'] for repo in repos_payload]

            self.assertEqual(repos, expected_repos)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                'https://api.github.com/orgs/google/repos'
            )

    @patch('client.get_json')
    def test_public_repos_with_license(self, mock_get_json):
        """Test public_repos with license filtering."""
        mock_get_json.return_value = repos_payload

        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = (
                'https://api.github.com/orgs/google/repos'
            )

            client = GithubOrgClient('google')
            repos = client.public_repos(license='apache-2.0')

            self.assertEqual(repos, apache2_repos)
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(
                'https://api.github.com/orgs/google/repos'
            )


if __name__ == '__main__':
    unittest.main()
