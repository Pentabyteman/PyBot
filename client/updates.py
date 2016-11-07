# This file should automatically check for updates.

from urllib import request


def check_for_updates(version):
    print("Checking for updates")
    url = "https://github.com/Pentabyteman/PyBot/releases/latest"
    current_version = version_number(version)

    res = request.urlopen(url)
    final_url = res.geturl()

    tag = final_url.split("/")[-1]
    latest = tag.split("v")[-1]
    return version_number(latest) > current_version


def version_number(string):
    version = string.split(".")
    try:
        return int("".join(version))
    except ValueError:
        return 0
