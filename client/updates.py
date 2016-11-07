# This file should automatically check for updates.
# 
#
import settings
import urllib.request

def check_for_updates():
  print("Checking for updates")
  tag_liste = []
  url = "www.github.com/Pentabyteman/PyBot/releases/tag"
  currentversion = settings.get_standard_settings()[3]
  major, minor, smallest = currentVersion.split['.']
  new_tag1 = "{}.{}.{}".format(major+1, minor, smallest)
  tag_liste.append(new_tag1)
  new_tag2 = "{}.{}.{}".format(major, minor+1, smallest)
  tag_liste.append(new_tag2)
  new_tag3 = "{}.{}.{}".format(major, minor smallest+1)
  tag_liste.append(new_tag3)
  for tag in tag_liste:
    try:
      checking_url = str(url + tag)
      if str(urllib.request.urlopen(checking_url).getcode()) != "200":
        print("NOTICE: UPDATE AVAILABLE")
        return "update"
   except:
      pass
  print("No updates available")
  
