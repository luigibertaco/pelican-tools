import argparse
import datetime
import getpass
import os
import shutil
import sys
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


def main():
    parser = argparse.ArgumentParser(description="An article creator for Pelican")

    parser.add_argument("title", help="The article title")
    parser.add_argument(
        "-a",
        "--author",
        default=DEFAULT_AUTHOR,
        help=f"The author of the article (default: `{DEFAULT_AUTHOR}`)",
    )
    parser.add_argument(
        "-t", "--tags", default="", help="Add tags to the article (separated by comma)",
    )
    parser.add_argument("-c", "--category", help="Set the article category")
    parser.add_argument(
        "-s",
        "--slug",
        help="Define the article slug (default: generates slug from title)",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="content/posts",
        help="Path to save the article file (default: `content/posts`)",
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
    args = parser.parse_args()

    if args.markup.lower() not in ACCEPTED_MARKUPS:
        raise ValueError(
            "%s is not a valid markup format, availabe options are %s " %
            (args.markup, ", ".join(ACCEPTED_MARKUPS)),
        )

    file_dir = Path() / args.path

    slug = slugify(args.slug if args.slug else args.title).replace(" ", "-")
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    tags = args.tags.split(",")

    if args.markup.lower() == "md":
        ext = ".md"
        header_generator_fn = build_markdown_header
    else:
        ext = ".rst"
        header_generator_fn = build_header

    file_path = file_dir / (slug + ext).replace("-", "_")
    header = header_generator_fn(
        args.title, date, args.author, [args.category], tags, slug
    )

    with open(file_path, "w") as article_file:
        article_file.write(header)

    print('Article file created at %s' % file_path)
