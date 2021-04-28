#!/usr/bin/env python3
import json
import re
import sys
import time
import random
import argparse

from requests import Session

from ddns import simulate_ddns_router
from misc import pos, neg

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 " \
             "Safari/537.36 Edg/90.0.818.49 "

HEADER_REFERER = "https://my.noip.com/"
HEADER_ORIGIN = "https://my.noip.com"

HOSTNAME_TOUCH_URL = "https://my.noip.com/api/host/%s/touch"
HOSTNAME_PUT_URL = "https://my.noip.com/api/host/%s"
HOSTNAME_LIST_URL = "https://my.noip.com/api/host"

URL_DYNAMIC_DNS_PAGE = "https://my.noip.com/#!/dynamic-dns"
URL_LOGIN_PAGE = "https://www.noip.com/login"

EXTRACTOR_CSRF_TOKEN = re.compile(r"<meta id=\"token\" name=\"token\" content=\"(.+?)\">")
EXTRACTOR_LOGIN_TOKEN = re.compile(r"name=\"_token\" *?value=\"(.*?)\"")

TOKEN_RATE_LIMITED = "Your account has been locked due to excessive password entry failures."
TOKEN_LOGIN_SUCCESS = "My No-IP"


def main() -> None:
    parser = argparse.ArgumentParser(description="HASS - NoIP Hostname Automation System Script",
                                     epilog="Developed 2020 - 2021 by Flesh-Network developers.")

    parser.add_argument("username", type=str, help="the username of the NoIP account")
    parser.add_argument("password", type=str, help="the password of the NoIP account")

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("-r", "--renew", action="store_true",
                              help="simulate website access to renew all hostnames")

    action_group.add_argument("-u", "--update", type=str,
                              help="simulate website access to update hostname")

    action_group.add_argument("-l", "--loop", type=str, nargs="+",
                              help="simulate a ddns router for all hostnames")

    parser.add_argument("-j", "--jitter", action="store_true", help="add a random delay to avoid detection")
    parser.add_argument("-a", "--address", type=str, help="the ip to update the hostname with",
                        required="-u" in sys.argv or "--update" in sys.argv)

    parsed_args = parser.parse_args()

    if parsed_args.jitter:
        jitter_minutes = random.randint(1, 60)
        pos(f" Jittering for {jitter_minutes} minutes...")
        time.sleep(jitter_minutes * 60)

    pos("Starting No-IP scraper...")
    with login(parsed_args.username, parsed_args.password) as session:
        hostnames = get_hostnames(session)
        show_hostnames(hostnames)

        if parsed_args.renew:
            renew_hostnames(session, hostnames)

        elif parsed_args.update:
            update_hostname(session, hostnames, parsed_args.update, parsed_args.address)

        elif parsed_args.loop:
            simulate_ddns_router(session, parsed_args.loop, hostnames)

        pos("Closing session, all done!")


def login(username: str, password: str) -> Session:
    session = Session()

    # Obtain a CSRF token
    token_response = session.get(URL_LOGIN_PAGE)
    token = EXTRACTOR_LOGIN_TOKEN.search(token_response.text).group(1)

    pos(f"Extracted login token \"{token}\".")
    pos(f"Logging in as \"{username}\"...")
    login_response = session.post(URL_LOGIN_PAGE, data={
        "username": username,
        "password": password,
        "_token": token,
    })

    if TOKEN_RATE_LIMITED in login_response.text:
        neg("Rate limited.")
        sys.exit(-1)

    if TOKEN_LOGIN_SUCCESS not in login_response.text:
        neg("Login failed.")
        sys.exit(-1)

    main_page_response = session.get(URL_DYNAMIC_DNS_PAGE)
    csrf_token = EXTRACTOR_CSRF_TOKEN.search(main_page_response.text).group(1)

    # Set up some disguise headers.
    # We might get an "403 - Unauthorized" without this.
    session.headers["X-Requested-With"] = "XMLHttpRequest"
    session.headers["X-CSRF-TOKEN"] = csrf_token
    session.headers["Referer"] = HEADER_REFERER
    session.headers["Origin"] = HEADER_ORIGIN
    session.headers["User-Agent"] = USER_AGENT

    pos(f"Extracted CSRF token \"{csrf_token}\".")
    pos("Login succeeded.")
    return session


def get_hostnames(session: Session) -> list:
    pos("Requesting hostnames...")
    hostname_response = session.get(HOSTNAME_LIST_URL)
    return hostname_response.json()["hosts"]


def show_hostnames(hostnames: list) -> None:
    pos("Fetched hostnames:")
    for hostname in hostnames:
        pos(f" * Hostname targeting \"{hostname['target']}\": \"{hostname['hostname']}\", " +
            f"expiring soon: {hostname['is_expiring_soon']}: " +
            f"{hostname['days_remaining']} days, {hostname['hours_remaining']} hours remaining.")


def renew_hostnames(session: Session, hostnames: list) -> None:
    hostnames_to_renew = [name for name in hostnames if name["is_expiring_soon"]]

    if not hostnames_to_renew:
        pos("No hostnames to renew!")
        return

    pos("Renewing hostnames:")
    for hostname in hostnames_to_renew:
        pos(f" * Renewing: \"{hostname['hostname']}\"!")
        session.get(HOSTNAME_TOUCH_URL % hostname["id"])


def update_hostname(session: Session, hostnames: list, target_hostname_name: str, new_ip: str) -> None:
    target_hostnames = [hostname for hostname in hostnames if hostname["hostname"] == target_hostname_name]
    if not target_hostnames:
        neg(f"No hostname called \"{target_hostname_name}\"!")
        return

    pos(f"Updating hostname \"{target_hostname_name}\" to point to \"{new_ip}\".")
    target_hostname = target_hostnames[0]
    target_hostname["target"] = new_ip

    url = HOSTNAME_PUT_URL % target_hostname["id"]
    response = session.put(url, json.dumps(target_hostname), headers={
        "Content-Type": "application/json"
    })

    if response.status_code == 200:
        pos("Success.")

    else:
        neg("Failure.")


if __name__ == "__main__":
    main()
