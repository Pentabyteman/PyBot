#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sysconfig
import json

DEFAULT_SETTINGS = {"updating": "none", "username": "", "host": "",
                    "version": "1.0.0", "password": ""}


def get_pybot_platform():
    platform = str(sysconfig.get_platform())
    return platform


def get_python_version():
    python_vers = str(sysconfig.get_python_version())
    return python_vers


def get_standard_settings():
    """This function returns the standard settings as a list"""
    try:
        with open('resources/settings.json', 'r') as text:
            return json.load(text)
    except Exception as e:
        print("ERROR: Settings not readable. Forcing default settings.", e)
        return DEFAULT_SETTINGS


def write_standard_settings(settings):
    with open('resources/settings.json', 'w+') as f:
        json.dump(settings, f)


def update_standard_settings(settings):
    try:
        if settings["updating"] == 'none':
            # TODO: Get a tkinter dialogue field that actually enables the user
            # to change updating to never or always
            # if tkinter.messagebox.askyesno(
            # 'Update Settings',
            # 'Do you want to update your server settings'):
            # write_standard_settings(settings)
            write_standard_settings(settings)

        elif settings["updating"] == 'always':
            write_standard_settings(settings)
    except Exception as e:
        print("FATAL ERROR: Settings not writable.", e)
