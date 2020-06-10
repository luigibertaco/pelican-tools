"""Command line script that generates new article files.
"""

import argparse
from datetime import datetime
import getpass
import sys
from pathlib import Path

import click
from pelican.tools.pelican_import import build_header, build_markdown_header
from pelican.utils import slugify
import PyInquirer

MARKUP_CHOICES = ["md", "rst"]
TYPE_CHOICES = ["article", "page"]
STATUS_CHOICES = ["draft", "hidden", "published"]
DEFAULT_AUTHOR = getpass.getuser()

try:
    from markdown import Markdown
except ImportError:
    DEFAULT_MARKUP = "rst"
else:
    DEFAULT_MARKUP = "md"


def validate(markup, **parsed_args):
    """Validates the parsed arguments and raises appropriated exceptions for
    the validation issues found.

    Args:
        parsed_args: The parsed arguments received from the system.
    """

    if markup.lower() not in MARKUP_CHOICES:
        raise ValueError(
            "%s is not a valid markup format, available options are %s "
            % (markup, ", ".join(MARKUP_CHOICES)),
        )


def generate_article(
    content_type,
    title,
    slug=None,
    tags=None,
    markup=None,
    category=None,
    author=None,
    path=None,
    status=None,
    **kwargs,
):
    """Generates the article values from the validated parsed arguments.

    Args:
        validate_args: The validated arguments.

    Returns:
        file_content
        file_path
    """

    slug = slugify(slug or title).replace(" ", "-")

    if markup.lower() == "md":
        header_generator_fn = build_markdown_header
    else:
        header_generator_fn = build_header

    if content_type == "article":
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
    else:
        date = None

    file_content = header_generator_fn(
        title,
        date,
        author,
        [category] if category else None,
        tags.split(",") if tags else None,
        slug,
        status,
    )

    file_dir = Path() / path
    file_path = file_dir / f"{slug}.{markup}"

    return file_content, file_path


def review(file_content):
    questions = [
        {
            "type": "editor",
            "name": "content",
            "message": "Review",
            "default": file_content,
            "eargs": {"editor": "default", "ext": ".rst"},
        }
    ]
    answer = PyInquirer.prompt(questions)
    return answer["content"]


def save_file(file_content, file_path):
    """Saves the article file.

    Args:
        file_path: A string for the file path or a Path() like object.
        file_content: A string with the content of the file to be saved.
    """

    with open(file_path, "w") as article_file:
        article_file.write(file_content)

    print("Article file created at %s" % file_path)


def interactive(values):
    type_choices = sorted(TYPE_CHOICES, key=lambda x: x != values.get("content_type"))
    markup_choices = sorted(MARKUP_CHOICES, key=lambda x: x != values.get("markup"))
    status_choices = sorted(STATUS_CHOICES, key=lambda x: x != values.get("status"))
    questions = [
        {
            "type": "list",
            "name": "content_type",
            "message": "Content Type:",
            "choices": type_choices,
        },
        {
            "type": "input",
            "name": "title",
            "message": "Content Title:",
            "default": values.get("title") or "",
            "validate": lambda text: bool(text) or "Must provide a title",
        },
        {
            "type": "input",
            "name": "author",
            "message": "Author name:",
            "default": values.get("author") or "",
        },
        {
            "type": "input",
            "name": "tags",
            "message": "Tags (comma separated):",
            "default": values.get("tags") or "",
        },
        {
            "type": "input",
            "name": "category",
            "message": "Category:",
            "default": values.get("category") or "",
        },
        {
            "type": "input",
            "name": "slug",
            "message": "Slug:",
            "default": values.get("slug") or "",
        },
        {
            "type": "list",
            "name": "status",
            "message": "Status:",
            "choices": status_choices,
        },
        {
            "type": "list",
            "name": "markup",
            "message": "Markup Style:",
            "choices": markup_choices,
        },
    ]
    answers = PyInquirer.prompt(questions)

    path_prompt = [
        {
            "type": "input",
            "name": "path",
            "message": "File path:",
            "default": f"{values['path']}/{answers['content_type']}s",
        },
    ]
    path_answer = PyInquirer.prompt(path_prompt)

    return {**answers, **path_answer}


@click.command()
@click.option("--title", help="The article title.")
@click.option(
    "--content-type",
    type=click.Choice(TYPE_CHOICES),
    help="The content type to be created.",
)
@click.option(
    "--author",
    default=DEFAULT_AUTHOR,
    help=f"Set the author of the article. (default: `{DEFAULT_AUTHOR}`)",
)
@click.option(
    "--tags", default="", help="Set tags to the article. (separated by comma).",
)
@click.option("--category", help="Set the article category.")
@click.option(
    "--slug", help="Set a custom article slug. (default: generates slug from title)",
)
@click.option(
    "--status", help="Publication status", type=click.Choice(STATUS_CHOICES),
)
@click.option(
    "--path",
    default="content",
    help="Path to save the article file. (default: `content/posts`)",
)
@click.option(
    "--markup",
    type=click.Choice(MARKUP_CHOICES),
    default=DEFAULT_MARKUP,
    help=(
        "The markup style for the article. "
        f"Accepts: {', '.join(MARKUP_CHOICES)}. "
        "If the `markdown` package is installed defaults to `md`, "
        "otherwise, defaults to `rst`."
    ),
)
@click.option(
    "--prompt/--noprompt", default=True, help="Disable interactive prompt",
)
def main(prompt, **kwargs):
    """Generates a new article or page file from command line.
    """
    parsed_args = interactive(kwargs) if prompt else kwargs
    validate(**parsed_args)
    file_content, file_path = generate_article(**parsed_args)
    file_content = review(file_content) if prompt else file_content
    save_file(file_content, file_path)
