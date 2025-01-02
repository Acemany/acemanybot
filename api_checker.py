#!/usr/bin/env python3

from requests.exceptions import ReadTimeout
from requests import get
import click


@click.command()
def main():
    "Checks APIs that bot uses"

    apis = {
        "TheCatAPI": "http://api.thecatapi.com/",
        "cataas": "http://cataas.com/api/count",
        "TheDogAPI": "http://api.thedogapi.com/",
        "RandomFox": "http://randomfox.ca/floof",
        "Nekos.best": "http://nekos.best/api/v2/endpoints",
        "Safebooru": "http://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit=1",
        "NekosApi": "http://api.nekosapi.com/v3/images/random?limit=1",
    }

    for name, lnk in apis.items():
        try:
            resp = get(lnk, proxies={'http': 'socks5://0.0.0.0:1080',
                                     'https': 'socks5://0.0.0.0:1080'},
                       timeout=5)
            text: str = resp.text
            code: int = resp.status_code
            time: float = resp.elapsed.total_seconds()
        except ReadTimeout:
            text: str = "Read timed out"
            code: int = 598
            time: float = 5

        click.echo(
            click.style(f'[{code}]{name} ', fg=('grey', 'green', 'yellow', 'red', 'bright_red')[code//100-1]) +
            f'{int(time*1000)}ms ' +
            (text if code > 399 else 'OK')
        )


if __name__ == "__main__":
    main()
