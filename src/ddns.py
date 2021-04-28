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


def ddns_set_hostname(session: Session, hostname_name: str, ip: str) -> None:
    pos(f"({datetime.now()}) Updating hostname \"{hostname_name}\" to point to \"{ip}\".")
    url = URL_DDNS_UPDATE % (hostname_name, ip)
    session.get(url)


def verify_hostnames_exist(hostname_names: list, hostnames: list) -> None:
    existing_hostnames = [hostname for hostname in hostnames if hostname["hostname"] in hostname_names]
    if len(hostname_names) != len(existing_hostnames):
        neg("Hostnames do not exist.")
        sys.exit(-1)


def simulate_ddns_router(session: Session, hostname_names: list, hostnames: list) -> None:
    verify_hostnames_exist(hostname_names, hostnames)
    get_ip = IPGetter()
    old_ip = None

    pos("Entering DDNS loop.")
    while True:
        time.sleep(random.randint(10, 60))
        if (new_ip := get_ip()) == old_ip:
            continue

        old_ip = new_ip
        for hostname_name in hostname_names:
            ddns_set_hostname(session, hostname_name, new_ip)
