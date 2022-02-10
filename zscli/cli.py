"""Console script for zscli."""

import json
import sys
from pathlib import Path

import click
import requests

from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"

CERTIFICATE_STATUS = [
    "all",
    "draft",
    "pending_validation",
    "issued",
    "cancelled",
    "expiring_soon",
    "expired",
]


class API:
    def __init__(self, debug, api_key, limit, page, verbose):
        self.debug = debug
        self.api_key = api_key
        self.limit = limit
        self.page = page
        self.verbose = verbose
        self.url = "https://api.zerossl.com"

    def _url(self, path):
        return f"{self.url}/{path}"

    def _params(self, extra={}):
        params = {
            "access_key": self.api_key,
            "limit": self.limit,
            "page": self.page,
        }
        params.update(extra)
        return params

    def _get(self, path, extra={}):
        return self._parse(requests.get(self._url(path), self._params(extra)))

    def _parse(self, response):
        if not response.ok:
            raise RuntimeError(f"API call failed: {response.text}")
        self.data = response.json()
        return self.data

    def list(self, status, search_text):
        if status == "all":
            status = ",".join(CERTIFICATE_STATUS)

        params = {"certificate_status": status}
        if search_text:
            params["search"] = search_text

        response = self._get("certificates", params)
        if "results" not in response:
            raise RuntimeError(f"no results in API response: {response}")

        certs = response["results"]

        if not self.verbose:
            certs = [
                {
                    "common_name": c["common_name"],
                    "status": c["status"],
                    "id": c["id"],
                }
                for c in certs
            ]

        return certs

    def download(self, _id, cross_signed, output_dir):
        if cross_signed:
            params = {"include_cross_signed": 1}
        else:
            params = {}
        files = self._get(f"certificates/{_id}/download/return", params)
        ret = []
        for name, content in files.items():
            cert_file = output_dir / name
            cert_file.write_text(content)
            ret.append(cert_file)
        return ret


def _output(output, data):
    output.write(json.dumps(data, indent=2) + "\n")


@click.group(name="zscli")
@click.version_option(message=header)
@click.option("-d", "--debug", is_flag=True, help="debug mode")
@click.option(
    "-k",
    "--api-key",
    type=str,
    envvar="ZEROSSL_API_KEY",
    help="ZEROSSL API key",
)
@click.option(
    "-l", "--limit", type=int, default=100, help="number of results per page"
)
@click.option(
    "-p",
    "--page",
    type=int,
    default=1,
    help="page number of results to return",
)
@click.option(
    "-v/-b",
    "--verbose/--brief",
    is_flag=True,
    default=False,
    help="increase output detail",
)
@click.pass_context
def cli(ctx, debug, api_key, limit, page, verbose):

    ctx.obj = API(debug, api_key, limit, page, verbose)

    def exception_handler(
        exception_type, exception, traceback, debug_hook=sys.excepthook
    ):

        if debug:
            debug_hook(exception_type, exception, traceback)
        else:
            click.echo(f"{exception_type.__name__}: {exception}", err=True)

    sys.excepthook = exception_handler

    return 0


@cli.command("ls")
@click.option(
    "-s",
    "--status",
    type=click.Choice(CERTIFICATE_STATUS),
    default="all",
    help="type of certificate to list",
)
@click.option(
    "-t", "--text", type=str, default=None, help="text search string"
)
@click.argument("output", type=click.File(mode="w"), default="-")
@click.pass_context
def ls(ctx, status, text, output):
    _output(output, ctx.obj.list(status, text))


@cli.command("download")
@click.option(
    "-i", "--id", "_id", type=str, required=True, help="certificate id"
)
@click.option(
    "-x/-X",
    "--cross-signed/--no-cross-signed",
    is_flag=True,
    default=True,
    help="include cross-signed certificate",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(
        exists=True,
        dir_okay=True,
        file_okay=False,
        writable=True,
        path_type=Path,
    ),
    default=".",
    help="directory where output files will be written",
)
@click.pass_context
def download(ctx, _id, cross_signed, output_dir):
    files = ctx.obj.download(_id, cross_signed, output_dir)
    for f in files:
        click.echo(str(f))


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
