# Load Order Library MO2 Plugin

**NOTE:** This plugin is **_NOT_** ready for actual use! Functionality is missing, and API tokens currently get stored inside of `ModOrganizer.ini` since it is a plugin setting, which is insecure.

The purpose of this plugin is to use the Load Order Library API to allow Mod Organizer 2 users to upload/update their currently selected to Load Order Library. It gets the current game MO2 is managing and uploads the currently selected profile.

For now, I'm only comfortable saying Bethesda games are "officially" supported, I have no idea how the other games work with MO2, please report any issues with any games you come across! That said, the plugin should auto detect whatever game is being managed.

# Using an API Token

Using an API token is only necessary if you want to update lists. To get one, please see the relevant Docs section https://docs.loadorderlibrary.com/en/authentication

Without an API token, every single upload will create a new list as updating anonymous lists is not possible.

# Settings

Use the plugin settings in MO2 to configure things like the list name, version, private, etc.
The defaults are as follows:

| Setting          | Default                 |
| ---------------- | ----------------------- |
| list_name        | My List                 |
| list_version     | 0.0.1                   |
| list_description |                         |
| list_website     |                         |
| list_discord     |                         |
| list_readme      |                         |
| list_private     | False                   |
| upload_files     | modlist.txt,plugins.txt |

For files to upload, add them separated by a comma like the default. A list requires at least one file to be uploaded.

# A Caveat with Profiles

The plugin does not currently support uploading profiles as separate lists if using an API token. Whatever profile you have active at the time is what will replace the list the plugin is tracking.
