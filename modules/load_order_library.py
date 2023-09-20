import mimetypes
import os
import json
import urllib.parse
import urllib.request as request

VERSION = "1.0.0"
BASE_URI = "https://api.loadorderlibrary.com/v1"
LISTS_URI = BASE_URI + "/lists"


class LolUpload:
    _apiToken = None
    _slug = None
    _gameIds = {
        "Cyberpunk 2077": 11,
        "Dark Messiah of Might & Magic": 13,
        "Dark Souls": 14,
        "Darkest Dungeon": 12,
        "Dragon Age II": 15,
        "Dragon Age: Origins": 16,
        "Dungeon Siege II": 17,
        "Enderal": 28,
        "Enderal SE": 29,
        "Fallout 3": 6,
        "Fallout 4": 8,
        "Fallout 4 VR": 9,
        "Fallout New Vegas": 7,
        "Kerbal Space Program": 18,
        "Kingdom Come: Deliverance": 19,
        "Mirror's Edge": 20,
        "Mount & Blade II: Bannerlord": 21,
        "No Man's Sky": 22,
        "STALKER Anomaly": 23,
        "Stardew Valley": 24,
        "Starfield": 30,
        "Tale of Two Wastelands": 10,
        "Morrowind": 1,
        "Oblivion": 2,
        "Skyrim": 3,
        "Skyrim Special Edition": 4,
        "Skyrim VR": 5,
        "The Binding of Isaac: Rebirth": 25,
        "The Witcher 3: Wild Hunt": 26,
        "Zeus and Poseidon": 27,
    }

    def __init__(self, plugin, apiToken=None, slug=None):
        self._plugin = plugin
        self._apiToken = apiToken
        self._slug = slug

    def upload(self):
        # User is using a token, so they probably want to
        # update a list if a slug is present.
        if self._apiToken is not None and self._slug is not None:
            return self.updateList(self._plugin)
        else:
            return self.createList(self._plugin)

    def updateList(self, plugin):
        url = f"{LISTS_URI}/{self._slug}"

        data = {
            "name": plugin.getSetting("list_name"),
            "game": str(self._gameIds[plugin._organizer.managedGame().gameName()]),
            "version": plugin.getSetting("list_version"),
            "description": plugin.getSetting("list_description"),
            "website": plugin.getSetting("list_website"),
            "discord": plugin.getSetting("list_discord"),
            "readme": plugin.getSetting("list_readme"),
            "private": "1" if bool(plugin.getSetting("list_readme")) else "0",
            "_method": "PUT",
        }

        files = []

        for file in plugin.getSetting("upload_files").split(","):
            files.append(f"{plugin._organizer.profile().absolutePath()}/{file}")

        # files = [
        #     plugin._organizer.profile().absoluteIniFilePath("modlist.txt"),
        #     plugin._organizer.profile().absoluteIniFilePath("plugins.txt"),
        # ]

        return self.sendPostRequest(url, data, files)

    def createList(self, plugin):
        url = LISTS_URI

        data = {
            "name": plugin.getSetting("list_name"),
            "game": str(self._gameIds[plugin._organizer.managedGame().gameName()]),
            "version": plugin.getSetting("list_version"),
            "description": plugin.getSetting("list_description"),
            "website": plugin.getSetting("list_website"),
            "discord": plugin.getSetting("list_discord"),
            "readme": plugin.getSetting("list_readme"),
            "private": "1" if bool(plugin.getSetting("list_readme")) else "0",
        }

        files = []

        for file in plugin.getSetting("upload_files").split(","):
            files.append(f"{plugin._organizer.profile().absolutePath()}/{file}")

        return self.sendPostRequest(url, data, files)

    def sendPostRequest(self, url, data, files):
        file_paths = files
        # Create a new HTTP POST request with multipart/form-data
        boundary = "----WebKitFormBoundaryLolMo2"
        data_bytes = b""
        for key, value in data.items():
            data_bytes += "--{}\r\n".format(boundary).encode("utf-8")
            data_bytes += 'Content-Disposition: form-data; name="{}"\r\n\r\n'.format(
                key
            ).encode("utf-8")
            data_bytes += "{}\r\n".format(value).encode("utf-8")
        for file_path in file_paths:
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = "application/octet-stream"
            file_name = os.path.basename(file_path)
            with open(file_path, "rb") as file:
                data_bytes += "--{}\r\n".format(boundary).encode("utf-8")
                data_bytes += 'Content-Disposition: form-data; name="files[]"; filename="{}"\r\n'.format(
                    file_name
                ).encode(
                    "utf-8"
                )
                data_bytes += "Content-Type: {}\r\n\r\n".format(mime_type).encode(
                    "utf-8"
                )
                data_bytes += file.read()
                data_bytes += b"\r\n"
        data_bytes += "--{}--\r\n".format(boundary).encode("utf-8")

        # Create a request object
        req = urllib.request.Request(url, data=data_bytes)
        req.method = "POST"

        req.headers = {
            "Accept": "application/json",
            "User-Agent": "lol-mo2-plugin/" + VERSION,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
        if self._apiToken:
            req.add_header("Authorization", "Bearer " + self._apiToken)

        try:
            # Send the request and get the response
            with request.urlopen(req) as response:
                response_data = response.read()
                # Process the response data as needed
                return json.loads(response_data.decode("utf-8"))
        except urllib.error.URLError as e:
            # Handle any errors here
            if hasattr(e, "read"):
                error_response_data = e.read()
                # Process the error response data as needed
                return json.loads(error_response_data.decode("utf-8"))
