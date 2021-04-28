import sys
import time
import random
from datetime import datetime
from itertools import cycle

import requests
from requests import Session

from misc import pos, neg

URL_DDNS_UPDATE = "https://dynupdate.no-ip.com/nic/update?hostname=%s&myip=%s"


class IPGetter:
    """ Use a variety of different services to get the system address. """

    __services = cycle([
        ("http://checkip.dyndns.org", lambda rsp: rsp.text.split(":")[1].split("<")[0].strip()),
        ("https://api.bigdatacloud.net/data/client-ip", lambda rsp: rsp.json()["ipString"]),
        ("http://ifconfig.me/all.json", lambda rsp: rsp.json()["ip_addr"]),
        ("https://freegeoip.app/json/", lambda rsp: rsp.json()["ip"]),
        ("https://api.ipify.org/", lambda rsp: rsp.text.strip()),
        ("https://ip.seeip.org/", lambda rsp: rsp.text.strip()),
        ("http://icanhazip.com/", lambda rsp: rsp.text.strip()),
        ("https://ipinfo.io", lambda rsp: rsp.json()["ip"])
    ])

    def __call__(self) -> str:
        url, func = next(self.__services)
        with requests.get(url) as rsp:
            return func(rsp)


def ddns_set_hostnames(session: Session, hostname_names: list, ip: str) -> None:
    pos(f"({datetime.now()}) Updating hostnames {hostname_names} to point to \"{ip}\".")
    url = URL_DDNS_UPDATE % (",".join(hostname_names), ip)
    if (rsp := session.get(url)).status_code != 200:
        neg(f"Error {rsp.status_code}")


def verify_hostnames_exist(hostname_names: list, hostnames: list) -> None:
    existing_hostnames = [hostname for hostname in hostnames if hostname["hostname"] in hostname_names]
    if len(hostname_names) != len(existing_hostnames):
        neg("Hostnames do not exist.")
        sys.exit(-1)


def simulate_ddns_router(session: Session, hostname_names: list, hostnames: list) -> None:
    verify_hostnames_exist(hostname_names, hostnames)
    get_ip = IPGetter()
    old_ip = None

    # Break the update sometimes
    del session.headers["X-Requested-With"]
    del session.headers["X-CSRF-TOKEN"]
    del session.headers["Referer"]
    del session.headers["Origin"]

    pos("Entering DDNS loop.")
    while True:
        time.sleep(random.randint(20, 80))
        if (new_ip := get_ip()) != old_ip:
            old_ip = new_ip
            ddns_set_hostnames(session, hostname_names, new_ip)
