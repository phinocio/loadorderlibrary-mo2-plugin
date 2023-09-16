# Load Order Library MO2 Plugin

**NOTE:** This plugin is **_NOT_** ready for actual use! Functionality is missing, and API tokens currently get stored inside of `ModOrganizer.ini` since it is a plugin setting, which is insecure.

The purpose of this plugin is to use the Load Order Library API to allow Mod Organizer 2 users to upload/update their currently selected to Load Order Library. It gets the current game MO2 is managing and uploads the currently selected profile.

# Limitations

Currently, the plugin _only_ uploads a new list each time. I will implement _updating_ a list once I add that functionality to the API itself.

API tokens are currently a plugin setting. This means they are then stored in `ModOrganizer.ini`, this is insecure as sometimes that file is shared. I am looking into a better place to store the API tokens.

The code is a mess. I need to split some functionality out into other files/classes, and map game names to IDs fully.
