import io
import textwrap
import unittest
from contextlib import redirect_stdout

from wgx import repo_config


class ParseSimpleYamlTests(unittest.TestCase):
    def test_ignores_yaml_document_markers(self) -> None:
        parsed = repo_config.parse_simple_yaml("---\nkey: value\n...\n")
        self.assertEqual(parsed, {"key": "value"})

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


class CliParserTests(unittest.TestCase):
    def test_build_parser_includes_expected_subcommands(self) -> None:
        parser = repo_config.build_parser()
        choices = parser._subparsers._group_actions[0].choices  # type: ignore[attr-defined]

        for command in ("mode", "owner", "repos", "ordered-repos"):
            self.assertIn(command, choices)

        repos_options = {
            option
            for action in choices["repos"]._actions  # type: ignore[attr-defined]
            for option in action.option_strings
        }
        self.assertIn("--json", repos_options)

    def test_repos_json_output(self) -> None:
        buffer = io.StringIO()
        data = {"repos": [{"name": "alpha"}, {"name": "beta"}]}

        with redirect_stdout(buffer):
            repo_config.cmd_repos(data, ordered=False, as_json=True)

        self.assertEqual(buffer.getvalue().strip(), '["alpha", "beta"]')


class ActiveFleetTruthTests(unittest.TestCase):
    def test_active_fleet_uses_core_and_projectable_static_entries(self) -> None:
        data = {
            "repos": [
                {"name": "core"},
                {"name": "disabled", "fleet": False},
            ],
            "static": {
                "include": [
                    {"name": "related", "status": "related"},
                    {"name": "donor", "status": "historical-donor", "fleet": False},
                ]
            },
        }
        self.assertEqual(repo_config.active_fleet_names(data), ["core", "related"])

    def test_active_fleet_rejects_duplicate_identity(self) -> None:
        data = {
            "repos": [{"name": "same"}],
            "static": {"include": [{"name": "same", "fleet": False}]},
        }
        with self.assertRaisesRegex(ValueError, "Duplicate Fleet repository"):
            repo_config.active_fleet_names(data)

    def test_archived_reference_must_be_non_fleet(self) -> None:
        data = {
            "repos": [],
            "static": {"include": [{"name": "old", "status": "archived-reference"}]},
        }
        with self.assertRaisesRegex(ValueError, "must set fleet: false"):
            repo_config.active_fleet_names(data)


if __name__ == "__main__":
    unittest.main()
