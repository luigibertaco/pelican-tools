"""Test cases for pelican-article module.
"""

import pytest
from pelican_tools.article import parse_args


@pytest.mark.parametrize("args,expected_data", [(["Article Title"], dict(title="Article Title")),])
def test_parse_args(args, expected_data):
    parsed_args = parse_args(args)
    assert parsed_args.__dict__ == expected_data
