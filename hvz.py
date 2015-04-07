#!/usr/bin/env python

# HVZ CLI

import click
import datetime
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
    url = "https://hvz.rit.edu/api/v1/test/key"
    params = {"apikey": key}
    r = requests.get(url, params=params)
    check_error(r)

    key_file = os.path.join(os.getenv("HOME"), ".hvz.api")
    with open(key_file, "w") as f_hnd:
        f_hnd.write(key)

    print("APIkey Set Successfully!")

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
    if response.status_code == 404:
        print("404 Not Found!")
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
@click.option("--human", prompt="Human ID", help='Human ID')
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

@main.command()
@click.option("--antivirus", prompt="Antivirus ID", help="Antivirus ID")
@click.option("--zombie", prompt="Zombie ID", help='Zombie ID')
def antivirus(antivirus, zombie):
    url = "https://hvz.rit.edu/api/v1/antivirus"
    params = {"apikey": api_get()}
    data = {"antivirus": antivirus, "zombie": zombie}
    r = requests.post(url, data=data, params=params)
    check_error(r)

    antivirus = r.json()
    print("{0} has used an antivirus!".format(antivirus["zombie_name"]))

@main.command("antivirus-valid")
def antivirus_valid():
    url = "https://hvz.rit.edu/api/v1/antivirus/valid_time"
    r = requests.get(url)

    if r.json()["result"]:
        print("An Antivirus CAN be used at this time")
    else:
        print("An Antivirus CAN NOT be used at this time")

@main.command()
def profile():
    url = "https://hvz.rit.edu/api/v1/profile"
    params = {"apikey": api_get()}
    r = requests.get(url, params=params)
    check_error(r)

    profile = r.json()["profile"]

    print("ID: " + str(profile["id"]))
    print("APIkey: " + profile["apikey"])
    print("Name: " + profile["fullname"])
    print("Email: " + profile["email"])
    if not profile["clan"] is None:
        print("Clan: " + profile["clan"])

    print("Team: " + profile["team"])
    if len(profile["badges"]) > 0:
        print('Badges:')
        for badge in profile["badges"]:
            print("\tTitle: " + badge["name"])
            print("\tID: " + str(badge["id"]))
            print("\tDescription: " + badge["description"])

    if not profile["avatar"] is None:
        print("Avatar: " + profile["avatar"])

    print("Zombie Attributes")
    print("\tID: " + profile["zombieId"])
    print("\tHumans Tagged: " + str(profile["humansTagged"]))
    if len(profile["infections"]) > 0:
        print("Infections")
        for infection in profile["infections"]:
            print_infection(infection)

    print("Human IDs:")
    for id in profile["humanIds"]:
        print(id["id_string"] + " Active: " + str(id["active"]))

@main.command("set-clan")
@click.argument("clan")
def set_clan(clan):
    url = "https://hvz.rit.edu/api/v1/profile/clan"
    params = {"apikey": api_get()}
    data = {"clan": clan}
    r = requests.post(url, data=data, params=params)
    check_error(r)

    print("Clan Successfully Set!")

@main.command()
def status():
    url = "https://hvz.rit.edu/api/v1/status"
    r = requests.get(url)
    check_error(r)

    status = r.json()

    url = "https://hvz.rit.edu/api/v1/status/teams"
    r = requests.get(url)
    check_error(r)
    teams = r.json()

    if status["status"] == "no-game":
        print("No game available in the near future!")
        pass

    game = status["game"]
    print("Game Start: " + datetime.datetime.fromtimestamp(
          int(game["start"])).strftime('%Y-%m-%d %H:%M:%S'))

    print("Game End: " + datetime.datetime.fromtimestamp(
          int(game["end"])).strftime('%Y-%m-%d %H:%M:%S'))

    suffix = None
    if status["status"] == "pre-game":
        suffix = " Until Game Starts!"
    else:
        suffix = " Remaining in the game!"

    print(datetime.datetime.fromtimestamp(
          int(game["time"]["diff"])).strftime('%H:%M:%S') + suffix)

    print("Humans: " + str(teams['humans']))
    print("Zombies: " + str(teams['zombies']))

def print_player(profile):
    print("ID: " + str(profile["id"]))
    print("Name: " + profile["fullname"])
    if not profile["clan"] is None:
        print("Clan: " + profile["clan"])

    print("Team: " + profile["team"])
    if len(profile["badges"]) > 0:
        print('Badges:')
        for badge in profile["badges"]:
            print("\tTitle: " + badge["name"])
            print("\tID: " + str(badge["id"]))
            print("\tDescription: " + badge["description"])

    if not profile["avatar"] is None:
        print("Avatar: " + profile["avatar"])

    print("Zombie Attributes")
    print("\tHumans Tagged: " + str(profile["humansTagged"]))
    print("---")

if __name__ == "__main__":
    main()
