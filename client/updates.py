# This file should automatically check for updates.

from urllib import request
from threading import Thread


def _updates_check(version, finished=None):
    print("Checking for updates")
    url = "https://github.com/Pentabyteman/PyBot/releases/latest"
    current_version = version_number(version)

    res = request.urlopen(url)
    final_url = res.geturl()

    tag = final_url.split("/")[-1]
    latest = tag.split("v")[-1]
    available = version_number(latest) > current_version
    if finished is not None:
        finished(available)
    else:
        return available


def check_for_updates(version, finished=None):
    if finished is not None:
        t = Thread(target=_updates_check, args=(version, finished))
        t.deamon = True
        t.start()
    else:
        return _updates_check(version)


def version_number(string):
    version = string.split(".")
    try:
        return int("".join(version))
    except ValueError:
        return 0
