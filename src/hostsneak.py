import re
import sys

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

    print(f"[+]: Extracted token \"{token}\"")
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

    hostname_response = session.get("https://my.noip.com/api/host")
    return hostname_response.json()["hosts"]


def show_hostnames(hostnames: list) -> None:
    print("[+]: Fetched hostnames:")
    for hostname in hostnames:
        print(f"[+]: * Hostname: \"{hostname['hostname']}\"")


def renew_hostnames(hostnames: list) -> None:
    pass


def main() -> None:
    print("[+]: Starting No-IP scraper...")
    session = login("username", "password!")
    hostnames = get_hostnames(session)
    show_hostnames(hostnames)
    renew_hostnames(hostnames)
    session.close()


if __name__ == "__main__":
    main()
