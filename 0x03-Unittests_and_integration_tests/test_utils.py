#!/usr/bin/env python3
"""
Unit tests for utils module functions:
- access_nested_map
- get_json
- memoize decorator
"""

import unittest
from typing import Dict, Tuple
from unittest.mock import patch, Mock
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    TestCase for utils.access_nested_map function.
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map: dict, path: Tuple[str, ...], expected: object) -> None:
        """
        Test access_nested_map returns correct value for given nested_map and path.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map: dict, path: Tuple[str, ...], expected_key: str) -> None:
        """
        Test access_nested_map raises KeyError with the expected key message.
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """
    TestCase for utils.get_json function.
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url: str, test_payload: Dict) -> None:
        """
        Test that get_json returns the expected payload from a mocked HTTP GET call.
        """
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        with patch("utils.requests.get", return_value=mock_response) as mock_get:
            result = get_json(test_url)

        mock_get.assert_called_once_with(test_url)
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    TestCase for utils.memoize decorator.
    """

    def test_memoize(self) -> None:
        """
        Test that a_method is called only once when accessed twice through
        a memoized property.
        """

        class TestClass:
            def a_method(self) -> int:
                """
                A simple method returning 42.
                """
                return 42

            @memoize
            def a_property(self) -> int:
                """
                A memoized property wrapping a_method.
                """
                return self.a_method()

        test_obj = TestClass()
        with patch.object(test_obj, "a_method", wraps=test_obj.a_method) as mock_method:
            # Call a_property twice
            first = test_obj.a_property
            second = test_obj.a_property

            # a_method should be called only once due to memoization
            mock_method.assert_called_once()
            self.assertEqual(first, 42)
            self.assertEqual(second, 42)


if __name__ == "__main__":
    unittest.main()
