import mobase
import os
import json
import hashlib

from typing import List

from ..modules.load_order_library import LolUpload

try:
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtWidgets import QMessageBox
    from PyQt5.QtGui import QIcon
except:
    from PyQt6.QtCore import QCoreApplication
    from PyQt6.QtWidgets import QMessageBox
    from PyQt6.QtGui import QIcon


"""
This is the "base" plugin, the api_token.py plugin inherits from
this one. Meaning that we don't need to redefine a lot of 
methods present in here.
"""


class LolMo2Upload(mobase.IPluginTool):
    _organizer: mobase.IOrganizer
    _profile: mobase.IProfile
    _name = "Load Order Library Upload"
    _frontendUrl = "https://loadorderlibrary.com"
    _appDataDir = "LoadOrderLibrary"
    _dataFile = ""
    _apiToken = None
    _slug = None

    def __init__(self):
        super().__init__()

    def tr(self, str_):
        return QCoreApplication.translate(self._name, str_)

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer
        self._profile = organizer.profile()
        self._dataFile = (
            hashlib.md5(organizer.basePath().encode()).hexdigest() + "-data.json"
        )
        # Get API token from appdata
        self.loadData()
        return True

    def name(self) -> str:
        return self._name

    def author(self) -> str:
        return "Phinocio"

    def description(self) -> str:
        return self.tr("Allows uploading directly to Load Order Library.")

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(1, 3, 1, mobase.ReleaseType.FINAL)

    def isActive(self) -> bool:
        return self._organizer.pluginSetting(self.name(), "enabled")

    def settings(self) -> List[mobase.PluginSetting]:
        return [
            self.setSetting("enabled", "enable this plugin", True),
            self.setSetting("list_name", "The name of the list.", "My List"),
            self.setSetting("list_version", "The version of the list.", "0.0.1"),
            self.setSetting("list_description", "The description of the list.", ""),
            self.setSetting("list_website", "The website for the list.", ""),
            self.setSetting("list_discord", "The discord for the list.", ""),
            self.setSetting("list_readme", "The readme of the list.", ""),
            self.setSetting("list_private", "If the list is private or not.", False),
            self.setSetting(
                "upload_files",
                "A list of the files to upload",
                "modlist.txt,plugins.txt",
            ),
            self.setSetting(
                "version_auto_parsing",
                "Attempt to auto parse the version from a separator. Looks for semver format.",
                False,
            ),
        ]

    def display(self) -> None:
        self.showMessage()

    def tooltip(self) -> str:
        return "Upload current profile to Load Order Library"

    def displayName(self) -> str:
        return "Load Order Library/Upload"

    def icon(self) -> QIcon:
        return QIcon()

    def showMessage(self) -> None:
        self.loadData()  # Load it every time just in case.
        action = "create"
        profile = self._organizer.profile().name()
        listName = self.getSetting("list_name")
        listDesc = self.getSetting("list_description")
        listVer = self.getSetting("list_version")
        private = self.getSetting("list_private")
        website = self.getSetting("list_website")
        discord = self.getSetting("list_discord")
        readme = self.getSetting("list_readme")
        files = self.getSetting("upload_files")
        if self._apiToken and self._slug:
            action = "update"
        msg = QMessageBox()
        msg.setWindowTitle("Upload to Load Order Library")
        msg.setText(
            f"You are about to <b>{action}</b> the list <b>{listName}</b>.\
             \nActive profile: <b>{profile}</b>.\
             Click show details for more info. Press <b>OK</b> to <b>{action}</b> the list."
        )
        msg.setInformativeText(
            "If something goes wrong. Please report the issue to Phinocio on\
            <a href='https://discord.gg/K3KnEgrQE4'>Discord</a> or\
            <a href='https://github.com/phinocio/loadorderlibrary-mo2-plugin'>GitHub.</a>"
        )
        msg.setDetailedText(
            f'Name: {listName}\nVersion: {str(listVer)}\nDescription: {listDesc}\nWebsite: {(website if len(website) > 0 else "none")}\nDiscord: {discord}\nReadme: {readme}\nPrivate: {str(private)}\nFiles: {files}'
        )
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
        )

        msg.buttonClicked.connect(self.popup_button)

        msg.exec()

    def popup_button(self, i) -> None:
        if i.text() == "OK":
            lolUpload = LolUpload(self)  # Pass in the plugin
            list = lolUpload.upload()
            if "data" in list.keys():
                url = self._frontendUrl + list["data"]["links"]["url"]
                if self._apiToken is not None:
                    self._slug = list["data"]["slug"]
                    self.saveData()
                    # If the list was created and we don't
                    # load the data again, the user needs
                    # to restart MO2 for the slug to
                    # be populated.
                    self.loadData()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Information)
                msg.setWindowTitle("Success!")
                msg.setText("Success! Visit your list <a href=" + url + ">here.</a>")
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("Failue!")
                msg.setText(f'Upload failed: {list["message"]}')

            msg.exec()

    def getSetting(self, settingName) -> mobase.PluginSetting:
        return self._organizer.pluginSetting(self.name(), settingName)

    def setSetting(self, name, desc, default) -> mobase.PluginSetting:
        return mobase.PluginSetting(name, desc, default)

    def saveData(self) -> None:
        dir = os.path.join(os.getenv("LOCALAPPDATA"), self._appDataDir)
        file = os.path.join(dir, self._dataFile)
        try:
            if not os.path.exists(dir):
                os.mkdir(dir)

            data = {
                "apiToken": self._apiToken,
                "slug": self._slug,
                "basePath": self._organizer.basePath(),
            }
            with open(file, "w") as f:
                json.dump(data, f)
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("File Read Error!")
            msg.setText(f"Something went wrong reading the data file. {e}")
            msg.exec()
            raise

    def loadData(self) -> None:
        dir = os.path.join(os.getenv("LOCALAPPDATA"), self._appDataDir)
        file = os.path.join(dir, self._dataFile)
        try:
            if not os.path.exists(dir):
                os.mkdir(dir)
                self._apiToken = None
                self._slug = None
                return

            if os.path.isfile(file):
                with open(file, "r") as f:
                    data = json.load(f)
                    self._apiToken = data["apiToken"]
                    self._slug = data["slug"]
        except Exception as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("File Read Error!")
            msg.setText(f"Something went wrong reading the data file. {e}")
            msg.exec()
            raise
