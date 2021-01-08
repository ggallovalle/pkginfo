import itertools
import os

import click
from tabulate import tabulate
from glom import glom

from .langs_info import langs_info


@click.command()
@click.option("--lang", "-l", type=click.Choice(langs_info.keys()), required=True)
@click.option(
    "--dependency",
    "-d",
    type=click.Choice(["dev", "prod", "all"], case_sensitive=False),
    default="all",
)
@click.option("--for-completion", "-c", is_flag=True)
@click.option("--from", "-f", "_from", type=click.STRING)
def pkginfo(lang, dependency, for_completion, _from):
    fmt = "plain"
    if not _from == None:
        langs_info[lang]["file"] = f"{_from}/{langs_info[lang]['file']}"
    if not os.path.isfile(langs_info[lang]["file"]):
        raise click.FileError(langs_info[lang]["file"], hint="file doesn't exist")
    info = get_info(langs_info[lang])
    if for_completion:
        if dependency == "all":
            click.echo("\n".join(info["prod"].keys()))
            click.echo("\n".join(info["dev"].keys()))
        else:
            click.echo("\n".join(info[dependency].keys()))
    else:
        if dependency == "all":
            click.echo("PROD")
            click.echo(tabulate(as_table(info["prod"]), tablefmt=fmt))
            click.echo("DEV")
            click.echo(tabulate(as_table(info["dev"]), tablefmt=fmt))
        else:
            click.echo(tabulate(as_table(info[dependency]), tablefmt=fmt))


def get_info(lang_spec):
    ctx = {}
    ctx["data"] = deserialize(lang_spec["file"])
    ctx["prod"] = glom(ctx["data"], lang_spec["prod"])
    ctx["dev"] = glom(ctx["data"], lang_spec["dev"])
    return ctx


def as_table(dictionary):
    return [[key, dictionary[key]] for key in dictionary]


def deserialize(file_path):
    with open(file_path) as content:
        filename, file_extension = os.path.splitext(file_path)
        if file_extension == ".json":
            import json

            return json.load(content)
        if file_extension == ".toml":
            import toml

            return toml.load(content)
