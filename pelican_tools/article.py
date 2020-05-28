"""Command line script that generates new article files.
"""

import argparse
import datetime
import getpass
from pathlib import Path

from pelican.tools.pelican_import import build_header, build_markdown_header
from pelican.utils import slugify

ACCEPTED_MARKUPS = ["md", "rst"]
DEFAULT_AUTHOR = getpass.getuser()

try:
    from markdown import Markdown
except ImportError:
    DEFAULT_MARKUP = "rst"
else:
    DEFAULT_MARKUP = "md"


def validate(parsed_args):
    """Validates the parsed arguments and raises appropriated exceptions for
    the validation issues found.

    Args:
        parsed_args: The parsed arguments received from the system.
    """

    if parsed_args.markup.lower() not in ACCEPTED_MARKUPS:
        raise ValueError(
            "%s is not a valid markup format, available options are %s "
            % (parsed_args.markup, ", ".join(ACCEPTED_MARKUPS)),
        )


def generate_article(validated_args):
    """Generates the article values from the validated parsed arguments.

    Args:
        validate_args: The validated arguments.

    Returns:
        file_content
        file_path
    """

    slug = slugify(validated_args.slug or validated_args.title)
    slug = slug.replace(" ", "-")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tags = validated_args.tags.split(",")

    if validated_args.markup.lower() == "md":
        ext = ".md"
        header_generator_fn = build_markdown_header
    else:
        ext = ".rst"
        header_generator_fn = build_header

    file_content = header_generator_fn(
        validated_args.title,
        date,
        validated_args.author,
        [validated_args.category],
        tags,
        slug
    )

    file_dir = Path() / validated_args.path
    file_path = file_dir / (slug + ext).replace("-", "_")

    return file_content, file_path


def save_file(file_content, file_path):
    """Saves the article file.

    Args:
        file_path: A string for the file path or a Path() like object.
        file_content: A string with the content of the file to be saved.
    """

    with open(file_path, "w") as article_file:
        article_file.write(file_content)

    print("Article file created at %s" % file_path)


def parse_args():
    """Parses the command line string arguments.
    """

    parser = argparse.ArgumentParser(
        description="An article creator for Pelican"
    )

    parser.add_argument(
        "title",
        help="The article title."
    )
    parser.add_argument(
        "-a",
        "--author",
        default=DEFAULT_AUTHOR,
        help=f"Set the author of the article. (default: `{DEFAULT_AUTHOR}`)",
    )
    parser.add_argument(
        "-t",
        "--tags",
        default="",
        help="Set tags to the article. (separated by comma).",
    )
    parser.add_argument(
        "-c",
        "--category",
        help="Set the article category."
    )
    parser.add_argument(
        "-s",
        "--slug",
        help="Set a custom article slug. (default: generates slug from title)",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="content/posts",
        help="Path to save the article file. (default: `content/posts`)",
    )
    parser.add_argument(
        "-m",
        "--markup",
        default=DEFAULT_MARKUP,
        help=(
            "The markup style for the article. "
            f"Accepts: {', '.join(ACCEPTED_MARKUPS)}. "
            "If the `markdown` package is installed defaults to `md`, "
            "otherwise, defaults to `rst`."
        ),
    )

    return parser.parse_args()


def main():
    """Generates a new article file from command line string arguments.
    """
    parsed_args = parse_args()
    validate(parsed_args)
    file_content, file_path = generate_article(parsed_args)
    save_file(file_content, file_path)
