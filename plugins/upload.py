import mobase
import os
import json

from typing import List

from ..modules.load_order_library import LolUpload

from PyQt5.QtCore import QCoreApplication, qCritical, QDir, qDebug
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon


class LolMo2Upload(mobase.IPluginTool):
    _organizer: mobase.IOrganizer
    _profile: mobase.IProfile
    _name = "Load Order Library Upload"
    _apiUrl = "https://testing.loadorderlibrary.com"
    _appDataDir = "LoadOrderLibrary"
    _gameIds = {"Skyrim Special Edition": 4, "Starfield": 30}
    _apiToken = None
    _slug = None

    def __init__(self):
        super().__init__()

    def __tr(self, str_):
        return QCoreApplication.translate(self._name, str_)

    def init(self, organizer: mobase.IOrganizer):
        self._organizer = organizer
        self._profile = organizer.profile()
        # Get API token from appdata
        self.loadData()
        return True

    def name(self) -> str:
        return self._name

    def author(self) -> str:
        return "Phinocio"

    def description(self) -> str:
        return self.__tr("Allows uploading directly to Load Order Library.")

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(0, 0, 1, mobase.ReleaseType.ALPHA)

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

    def popup_button(self, i) -> None:
        if i.text() == "OK":
            lolUpload = LolUpload(self, self._apiToken, self._slug)
            list = lolUpload.upload()
            if "data" in list.keys():
                url = self._apiUrl + list["data"]["links"]["url"]
                if self._apiToken is not None:
                    self._slug = list["data"]["slug"]
                    print(self._slug)
                    self.saveData()
                    # If the list was created and we don't
                    # load the data again, the user needs
                    # to restart MO2 for the slug to
                    # be populated.
                    self.loadData()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Success!")
                msg.setText("Success! Visit your list <a href=" + url + ">here.</a>")
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Failue!")
                msg.setText(f'Upload failed: {list["message"]}')

            msg.exec_()
        print(i.text())

    def getSetting(self, settingName) -> mobase.PluginSetting:
        return self._organizer.pluginSetting(self.name(), settingName)

    def setSetting(self, name, desc, default) -> mobase.PluginSetting:
        return mobase.PluginSetting(name, desc, default)

    def saveData(self) -> None:
        dir = os.path.join(os.getenv("LOCALAPPDATA"), self._appDataDir)
        file = os.path.join(dir, "data.json")
        if not os.path.exists(dir):
            os.mkdir(dir)

        data = {"apiToken": self._apiToken, "slug": self._slug}
        print(self._slug)
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def loadData(self) -> None:
        dir = os.path.join(os.getenv("LOCALAPPDATA"), self._appDataDir)
        file = os.path.join(dir, "data.json")
        if not os.path.exists(dir):
            os.mkdir(dir)
            self._apiToken = None
            self._slug = None
            return

        if os.path.isfile(file):
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._apiToken = data["apiToken"]
                self._slug = data["slug"]