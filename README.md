# HASS
> The Hostname Automation System Script

## What is this?
This is a cron-able script to automatically renew your free [NoIP](https://www.noip.com/) hostnames.

## How to use

```bash
(venv) D:\Github\hass\src>hass.py --help
usage: hass.py [-h] [-j] username password

HASS - NoIP Hostname Automation System Script

positional arguments:
  username      the username of the NoIP account
  password      the password of the NoIP account

optional arguments:
  -h, --help    show this help message and exit
  -j, --jitter  add a random delay to avoid detection

Developed 2020 by Flesh-Network developers.
```
