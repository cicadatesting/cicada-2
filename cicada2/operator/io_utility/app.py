from typing import List

import click

from cicada2.operator.io_utility.transfer import transfer_files


@click.group()
def cli():
    pass


@cli.command("transfer")
@click.argument("transfers", nargs=-1)
def transfer_cmd(transfers: List[str]):
    # parse list of transfers
    for transfer in transfers:
        src_dest = transfer.split("==")

        assert (
            len(src_dest) >= 2
        ), f"source to destination mapping incomplete: {transfer}"

        transfer_files(src_dest[0], src_dest[1])


if __name__ == "__main__":
    cli()
