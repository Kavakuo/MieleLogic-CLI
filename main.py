#!/usr/bin/env python3
import requests, sys, os, pathlib
from colorama import Fore


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://mielelogic.com',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://mielelogic.com/',
}

absPath = pathlib.Path(__file__).resolve()
folder = os.path.dirname(absPath)
token_path = os.path.join(folder, 'token.txt')

session = requests.Session()
session.headers = headers

def doLogin():
    authenticated = False
    while not authenticated:    
        username = input("username: ")
        password = input("password: ")
        loginData = {
            'grant_type': 'password',
            'username': username.replace(" ", ""),
            'password': password,
            'client_id': 'YV1ZAQ7BTE9IT2ZBZXLJ',
            'scope': 'NO',
            'noexpire': '1'
        }

        response = session.post('https://sec.mielelogic.com/v3/token', data=loginData)
        if response.status_code >= 500:
            print("{}Something went wrong, is the website working? https://mielelogic.com {}".format(Fore.RED, Fore.RESET))
            sys.exit(1)
        elif response.status_code >= 400 and response.json()["error_description"] == "login.err.bad_credentials":
            print("{}Invalid credentials, try again.{}".format(Fore.RED, Fore.RESET))
            continue
        elif response.status_code >= 400:
            print("Something went wrong...\n{}".format(response.text))
            sys.exit(1)
        else:
            authenticated = True

        token = response.json()["access_token"]
        with open(token_path, "w", encoding="utf-8") as f:
            f.write(token)

        session.headers["Authorization"] = "Bearer {}".format(token)

def main():
    try:
        with open(token_path, 'r', encoding="utf-8") as f:
            token = f.read()
        headers["Authorization"] = "Bearer {}".format(token)
    except FileNotFoundError:
        doLogin()

    authenticated = False
    while not authenticated:
        response = session.get("https://api.mielelogic.com/v3/Country/NO/Laundry/9312/laundrystates?language=en")
        if response.status_code in [401, 402, 403]:
            doLogin()
            continue
        elif response.status_code >= 500:
            print("{}Something went wrong, is the website working? https://mielelogic.com {}".format(Fore.RED, Fore.RESET))
            return
        else:
            authenticated = True

        response = response.json()

    machines = response["MachineStates"]
    washingMachines = list(filter(lambda x: x["MachineSymbol"] == 0, machines))
    dryerMachines = list(filter(lambda x: x["MachineSymbol"] == 1, machines))
    print("Waschmaschine:")
    for i in washingMachines:
        state = "{} {}".format(i["Text1"].strip(), i["Text2"].strip()).replace("\n", " ")
        color = Fore.RED if i["MachineColor"] == 2 else Fore.GREEN
        print("  {color}{}: {}{colorE}".format(i["UnitName"], state, color=color,colorE=Fore.RESET))
    
    print("\nTrockner:")
    for i in dryerMachines:
        state = "{} {}".format(i["Text1"].strip(), i["Text2"].strip()).replace("\n", " ")
        color = Fore.RED if i["MachineColor"] == 2 else Fore.GREEN
        print("  {color}{}: {}{colorE}".format(i["UnitName"], state, color=color, colorE=Fore.RESET))

if __name__ == "__main__":
    main()
