# HASS
> The Hostname Automation System Script

## What is this?
This is a cron-able script to automatically renew and update your free [NoIP](https://www.noip.com/) hostnames.

## How to use?

```
(venv) D:\Github\hass\src>hass.py --help
usage: hass.py [-h] [-r | -u UPDATE | -l LOOP [LOOP ...]] [-j] [-a ADDRESS] username password

HASS - NoIP Hostname Automation System Script

positional arguments:
  username              the username of the NoIP account
  password              the password of the NoIP account

optional arguments:
  -h, --help            show this help message and exit
  -r, --renew           simulate website access to renew all hostnames
  -u UPDATE, --update UPDATE
                        simulate website access to update hostname
  -l LOOP [LOOP ...], --loop LOOP [LOOP ...]
                        simulate a ddns router for all hostnames
  -j, --jitter          add a random delay to avoid detection
  -a ADDRESS, --address ADDRESS
                        the ip to update the hostname with

Developed 2020 - 2021 by Flesh-Network developers.
```

## How to simulate a DDNS router?

```
hass.py <username> <password> --loop domain1.ddns.net domain2.ddns.net
```
