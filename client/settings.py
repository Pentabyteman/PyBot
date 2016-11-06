#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sysconfig


def get_pybot_platform():
    platform = str(sysconfig.get_platform())
    return platform


def get_python_version():
    python_vers = str(sysconfig.get_python_version())
    return python_vers

# TODO: get this done! @Pentabyteman @EirchHasl
def get_standard_settings():
    """This function returns the standard settings as a list"""
    ioStream = open('resources/settings.txt', 'rt', encoding="ISO-8859-15")
    text = str(ioStream)
    row_list = text.split('\n')
    settings_list = []
    for row in row_list:
        new_setting = row.split(': ')[1]
        settings_list.append(settings_list)
    return settings_list


def update_standard_settings(user=None, host=None):
    version = get_standard_settings()[2]
    new_doc = "USER: {0}\nHOST: {1}\nVERSION: {2}".format(user, host, version)
    open('resources/settings.text', 'w')
    # TODO: delete all content and write the new_doc


text = get_standard_settings()
print(text)
