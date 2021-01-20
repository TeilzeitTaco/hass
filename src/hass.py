#!/usr/bin/env python3

import re
import sys
import time
import random
import argparse

from requests import Session

LOGIN_TOKEN_EXTRACTOR = re.compile(r"name=\"_token\" *?value=\"(.*?)\"")

LOGIN_SUCCESS_TOKEN = "My No-IP"
LOGIN_RATE_LIMITED_TOKEN = "Your account has been locked due to excessive password entry failures."

HOSTNAME_LIST_URL = "https://my.noip.com/api/host"
LOGIN_URL = "https://www.noip.com/login"


def login(username: str, password: str) -> Session:
    session = Session()

    # Obtain a CSRF token
    token_response = session.get(LOGIN_URL)
    token = LOGIN_TOKEN_EXTRACTOR.search(token_response.text).group(1)

    print(f"[+]: Extracted token \"{token}\".")
    print(f"[+]: Logging in as \"{username}\"...")
    login_response = session.post(LOGIN_URL, data={
        "username": username,
        "password": password,
        "_token": token,
    })

    if LOGIN_RATE_LIMITED_TOKEN in login_response.text:
        print("[-]: Rate limited.")
        sys.exit(-1)

    if LOGIN_SUCCESS_TOKEN not in login_response.text:
        print("[-]: Login failed.")
        sys.exit(-1)

    print("[+]: Login succeeded.")
    return session


def get_hostnames(session: Session) -> list:
    print("[+]: Requesting hostnames...")

    # We get an "Unauthorized" without this and I hate it.
    session.headers["X-Requested-With"] = "XMLHttpRequest"

    hostname_response = session.get(HOSTNAME_LIST_URL)
    return hostname_response.json()["hosts"]


def show_hostnames(hostnames: list) -> None:
    print("[+]: Fetched hostnames:")
    for hostname in hostnames:
        print(f"[+]:  * Hostname targeting \"{hostname['target']}\": \"{hostname['hostname']}\", " +
              f"expiring soon: {hostname['is_expiring_soon']}: " +
              f"{hostname['days_remaining']} days, {hostname['hours_remaining']} hours remaining.")


def renew_hostnames(session: Session, hostnames: list) -> None:
    hostnames_to_renew = [name for name in hostnames if name["is_expiring_soon"]]

    if not hostnames_to_renew:
        print("[+]: No hostnames to renew!")
        return

    print("[+]: Renewing hostnames:")
    for hostname in hostnames_to_renew:
        print(f"[+]: * Renewing: \"{hostname['hostname']}\"")
        session.get("")
        # TODO: Implement!


def main() -> None:
    parser = argparse.ArgumentParser(description="HASS - NoIP Hostname Automation System Script",
                                     epilog="Developed 2020 by Flesh-Network developers.")

    parser.add_argument("username", type=str, help="the username of the NoIP account")
    parser.add_argument("password", type=str, help="the password of the NoIP account")
    parser.add_argument("-j", "--jitter", action="store_true", help="add a random delay to avoid detection")

    parsed_args = parser.parse_args()

    if parsed_args.jitter:
        jitter_minutes = random.randint(1, 60)
        print(f"[+]: Jittering for {jitter_minutes} minutes...")
        time.sleep(jitter_minutes * 60)

    print("[+]: Starting No-IP scraper...")
    session = login(parsed_args.username, parsed_args.password)
    hostnames = get_hostnames(session)
    show_hostnames(hostnames)
    renew_hostnames(session, hostnames)

    print("[+]: Closing session, all done!")
    session.close()


if __name__ == "__main__":
    main()
