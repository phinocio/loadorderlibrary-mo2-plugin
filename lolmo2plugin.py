import mobase
import urllib.parse
import urllib.request as request
import mimetypes
import os
import json

from typing import List

from PyQt5.QtCore import QCoreApplication, qCritical, QDir, qDebug
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon


class LolMo2Plugin(mobase.IPluginTool):
    _organizer: mobase.IOrganizer
    _profile: mobase.IProfile
    _name = "Load Order Library Upload"
    _gameIds = {"Skyrim Special Edition": 4, "Starfield": 30}

    def __init__(self):
        super().__init__()

    def __tr(self, str_):
        return QCoreApplication.translate(self._name, str_)

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer
        self._profile = organizer.profile()
        return True

    def name(self) -> str:
        return self._name

    def author(self) -> str:
        return "Phinocio"

    def description(self) -> str:
        return self.__tr("Allows uploading directly to Load Order Library.")

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(0, 0, 1, mobase.ReleaseType.ALPHA)

    def isActive(self):
        return self._organizer.pluginSetting(self.name(), "enabled")

    def settings(self) -> List[mobase.PluginSetting]:
        return [
            self.setSetting("enabled", "enable this plugin", True),
            self.setSetting("list_name", "The name of the list.", "My List"),
            self.setSetting("list_version", "The version of the list.", "0.0.1"),
            self.setSetting("list_private", "If the list is private or not.", False),
            self.setSetting("list_description", "The description of the list.", ""),
            self.setSetting("list_discord", "The discord for the list.", ""),
            self.setSetting("list_website", "The website for the list.", ""),
            self.setSetting("list_readme", "The readme of the list.", ""),
            self.setSetting("api_token", "The API token for auth.", ""),
        ]

    def display(self):
        self.showMessage()

    def tooltip(self):
        return "Upload current profile to Load Order Library"

    def displayName(self):
        return "Upload to Load Order Library"

    def icon(self):
        return QIcon()

    def showMessage(self):
        profile = self._organizer.profile().name()
        listName = self.getSetting("list_name")
        listDesc = self.getSetting("list_description")
        listVer = self.getSetting("list_version")
        private = self.getSetting("list_private")
        website = self.getSetting("list_website")
        discord = self.getSetting("list_discord")
        readme = self.getSetting("list_readme")
        msg = QMessageBox()
        msg.setWindowTitle("Upload to Load Order Library")
        msg.setText(
            "You are about to upload the list <b>"
            + listName
            + "</b> with profile <b>"
            + profile
            + "</b>. Click show details for more info. Press <b>OK</b> to upload."
        )
        msg.setInformativeText(
            'Uploading currently only creates <i>new</i> lists. If you want to update, go to <a href="https://loadorderlibrary.com">the site.</a>'
        )
        msg.setDetailedText(
            "Name: "
            + listName
            + "\nVersion: "
            + str(listVer)
            + "\nDescription: "
            + listDesc
            + "\nWebsite: "
            + (website if len(website) > 0 else "none")
            + "\nDiscord: "
            + discord
            + "\nReadme: "
            + readme
            + "\nPrivate: "
            + str(private)
        )
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        msg.buttonClicked.connect(self.popup_button)

        msg.exec_()

    def popup_button(self, i):
        if i.text() == "OK":
            list = self.uploadList()
            url = "https://testing.loadorderlibrary.com" + list["data"]["links"]["url"]
            msg = QMessageBox()
            msg.setWindowTitle("Success!")
            msg.setText("Success! Visit your list <a href=" + url + ">here.</a>")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
        print(i.text())

    def getSetting(self, settingName):
        return self._organizer.pluginSetting(self.name(), settingName)

    def setSetting(self, name, desc, default):
        return mobase.PluginSetting(name, desc, default)

    def uploadList(self):
        VERSION = "0.0.1"
        BASE_URI = "https://testingapi.loadorderlibrary.com/v1"
        LISTS_URI = BASE_URI + "/lists"

        data = {
            "name": self.getSetting("list_name"),
            "game": str(self._gameIds[self._organizer.managedGame().gameName()]),
            "description": self.getSetting("list_description"),
        }

        file_paths = [
            self._organizer.profile().absoluteIniFilePath("modlist.txt"),
            self._organizer.profile().absoluteIniFilePath("plugins.txt"),
        ]

        # Create a new HTTP POST request with multipart/form-data
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
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
        req = urllib.request.Request(LISTS_URI, data=data_bytes)
        req.method = "POST"

        # TODO: REMOVE FROM SETTINGS before full release. Setting values get
        # put into ModOrganizer.ini, making it insecure for tokens.
        req.headers = {
            "Accept": "application/json",
            "User-Agent": "lol-mo2-plugin/" + VERSION,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
        if len(self.getSetting("api_token")) > 0:
            req.add_header("Authorization", "Bearer " + self.getSetting("api_token"))

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
                print(error_response_data.decode("utf-8"))
