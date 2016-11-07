# This file should automatically check for updates.
# 
#
import settings
import urllib.request

UPDATE_DICTIONARY = {1 : [1, 0, 0], 2 : [1, 0, 1], 3: [1, 1, 1], 4 : [0, 1, 0], 5 : [0, 1, 1], 6 : [0, 0, 1]}


def check_for_updates():
    print("Checking for updates")
    tag_liste = []
    url = "https://github.com/Pentabyteman/PyBot/releases/tag/v"
    currentVersion = settings.get_standard_settings()[4]
    major, minor, smallest = currentVersion.split('.')
    for i in range(1, 7):
        new_tag = "{}.{}.{}".format(int(major)+UPDATE_DICTIONARY[i][0], int(minor)+UPDATE_DICTIONARY[i][1], int(smallest)+UPDATE_DICTIONARY[i][2])
        tag_liste.append(new_tag)
    for tag in tag_liste:
        try:
            checking_url = str(url + tag)
            if str(urllib.request.urlopen(checking_url).getcode()) == "200":
              print("NOTICE: UPDATE AVAILABLE")
              return "update"
        except Exception as e:
            pass
    #If we got to here, no update exists
    print("No updates available")
   
