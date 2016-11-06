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
    try:
        with open('resources/settings.txt', 'rt', encoding="ISO-8859-15") as text:
            text_content = text.read()
            row_list = text_content.split('\n')
            settings_list = []
            for row in row_list:
                new_setting = row.split(': ')[1]
                settings_list.append(new_setting)
            return settings_list
    except Exception as e:
        print("ERROR: Settings not readable. Forcing default settings.", e)
        settings_list = ['true', 'true', "", "", "2.0"]
        return settings_list


def update_standard_settings(user=None, host=None):
    try:
        if get_standard_settings()[0] == 'true':
            version = get_standard_settings()[3]
            new_doc = "PROMPTING: true\nEDIT_ENABLED: true\nUSER: {0}\nHOST: {1}\nVERSION: {2}".format(user, host,
                                                                                                       version)
            with open('resources/settings.txt', 'w') as text:
                text.seek(0)
                text.write(new_doc)
        else:
            pass
    except Exception as e:
        print("FATAL ERROR: Settings not writable.", e)

def disable_prompting():
    try:
        editable, user, host, version = get_standard_settings()
        new_doc = "PROMPTING: false\nEDIT_ENABLED: true\nUSER: {0}\nHOST: {1}\nVERSION: {2}".format(user, host, version)
        with open('resources/settings.txt', 'w') as text:
            text.seek(0)
            text.write(new_doc)
    except Exception as e:
        print("FATAL ERROR: Settings not writable.", e)

def disable_edits():
    try:
        editable, user, host, version = get_standard_settings()
        new_doc = "EDIT_ENABLED: false\nUSER: {0}\nHOST: {1}\nVERSION: {2}".format(user, host, version)
        with open('resources/settings.txt', 'w') as text:
            text.seek(0)
            text.write(new_doc)
    except Exception as e:
        print("FATAL ERROR: Settings not writable.", e)

def enable_edits():
    try:
        editable, user, host, version = get_standard_settings()
        new_doc = "EDIT_ENABLED: true\nUSER: {0}\nHOST: {1}\nVERSION: {2}".format(user, host, version)
        with open('resources/settings.txt', 'w') as text:
            text.seek(0)
            text.write(new_doc)
    except Exception as e:
        print("FATAL ERROR: Settings not writable.", e)