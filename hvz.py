#!/usr/bin/env python

# HVZ CLI

import click
import os
import requests
import sys

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

def api_get():
    key_file = os.path.join(os.getenv("HOME"), ".hvz.api")
    with open(key_file, "r") as f_hnd:
        api_key = f_hnd.read().strip()
    if api_key is None:
        sys.exit(1)
    return api_key

def check_error(response):
    if response.status_code == 400:
        errors = response.json()
        for error in errors["errors"]:
            print(error)
        sys.exit(1)

@main.command()
def rules():
    url = "https://hvz.rit.edu/api/v1/rules"
    r = requests.get(url)

    rules_data = r.json()

    for rule in rules_data['rulesets']:
        print(rule['title'])
        print(rule['body'])

if __name__ == "__main__":
    main()
