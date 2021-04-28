# HASS
> The Hostname Automation System Script

## What is this?
This is a cron-able script to automatically renew your free [NoIP](https://www.noip.com/) hostnames.

## How to use?

```bash
(venv) D:\Github\hass\src>hass.py --help
usage: hass.py [-h] [-r | -u UPDATE] [-j] [-a ADDRESS] username password

HASS - NoIP Hostname Automation System Script

positional arguments:
  username              the username of the NoIP account
  password              the password of the NoIP account

optional arguments:
  -h, --help            show this help message and exit
  -r, --renew
  -u UPDATE, --update UPDATE
                        the hostname to update
  -j, --jitter          add a random delay to avoid detection
  -a ADDRESS, --address ADDRESS
                        the ip to update the hostname with

Developed 2020 - 2021 by Flesh-Network developers.
```
