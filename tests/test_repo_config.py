import textwrap
import unittest

from wgx import repo_config


class ParseSimpleYamlTests(unittest.TestCase):
    def test_preserves_hash_characters_inside_quotes(self) -> None:
        yaml_text = textwrap.dedent(
            """
            key: "value # not a comment"
            key2: 'another # example'
            key3: plain # actual comment
            """
        )
        parsed = repo_config.parse_simple_yaml(yaml_text)
        self.assertEqual(
            parsed,
            {
                "key": "value # not a comment",
                "key2": "another # example",
                "key3": "plain",
            },
        )

    def test_preserves_numeric_like_strings_with_leading_zero(self) -> None:
        yaml_text = textwrap.dedent(
            """
            serial: 08
            pin: 00123
            offset: -08
            explicit: +0123
            """
        )
        parsed = repo_config.parse_simple_yaml(yaml_text)
        self.assertEqual(
            parsed,
            {
                "serial": "08",
                "pin": "00123",
                "offset": "-08",
                "explicit": "+0123",
            },
        )
        self.assertTrue(all(isinstance(value, str) for value in parsed.values()))

    def test_allows_nested_blocks_with_deeper_indent(self) -> None:
        yaml_text = textwrap.dedent(
            """
            root:
                - name: alpha
                  settings:
                      enabled: true
            """
        )
        parsed = repo_config.parse_simple_yaml(yaml_text)
        self.assertEqual(
            parsed,
            {
                "root": [
                    {
                        "name": "alpha",
                        "settings": {"enabled": True},
                    }
                ]
            },
        )

    def test_sequence_values_with_colons_are_not_interpreted_as_mappings(self) -> None:
        yaml_text = textwrap.dedent(
            """
            links:
              - https://example.com
              - ftp://example.org
            """
        )
        parsed = repo_config.parse_simple_yaml(yaml_text)
        self.assertEqual(
            parsed,
            {"links": ["https://example.com", "ftp://example.org"]}
        )

    def test_empty_values_are_interpreted_as_null(self) -> None:
        yaml_text = textwrap.dedent(
            """
            empty_mapping:
            another:
            explicit_empty: ""
            also_explicit: ''
            nested:
              value:
              with_default: provided
            list:
              -
              - item
              - ""
            """
        )
        parsed = repo_config.parse_simple_yaml(yaml_text)
        self.assertEqual(
            parsed,
            {
                "empty_mapping": None,
                "another": None,
                "explicit_empty": "",
                "also_explicit": "",
                "nested": {"value": None, "with_default": "provided"},
                "list": [None, "item", ""],
            },
        )


if __name__ == "__main__":
    unittest.main()
