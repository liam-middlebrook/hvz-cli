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

@main.command()
def missions():
    url = "https://hvz.rit.edu/api/v1/missions"
    data = {"apikey": api_get()}
    r = requests.get(url, params=data)
    check_error(r)

    missions_data = r.json()

    for mission in missions_data['missions']:
        print(mission['title'])
        print(mission['team'])
        print(mission['post_date'])
        print(mission['body'])

@main.command()
@click.option("--human" , prompt="Human ID", help='Human ID')
@click.option("--zombie", prompt="Zombie ID", help='Zombie ID')
@click.option("--latitude", default=None)
@click.option("--longitude", default=None)
def infect(human, zombie, latitude, longitude):
    url = "https://hvz.rit.edu/api/v1/register_infection"
    params = {"apikey": api_get()}
    data = {"human": human, "zombie": zombie,
            "latitude": latitude, "longitude": longitude}
    r = requests.post(url, data=data, params=params)
    check_error(r)

    infection = r.json()
    print("{0} has infected {1}!".format(infection["zombie_name"],
          infection["human_name"]))

if __name__ == "__main__":
    main()
