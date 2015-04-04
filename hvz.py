#!/usr/bin/env python

# HVZ CLI

import click
import os
import requests

@click.group()
def main():
    pass

@main.command("api-key")
@click.option("--key", prompt="Your HvZ API Key",
              help="You can find your API online!")
def api_set(key):
    key_file = os.path.join(os.getenv("HOME"), ".hvz.api")
    with open(key_file, "w") as f_hnd:
        f_hnd.write(key)

if __name__ == "__main__":
    main()
