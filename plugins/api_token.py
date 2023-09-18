import mobase
import os
import json
import hashlib

from typing import List

from .upload import LolMo2Upload

from PyQt5.QtCore import QCoreApplication, qCritical, QDir, qDebug
from PyQt5.QtWidgets import QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon


class LolMo2ApiToken(LolMo2Upload, mobase.IPluginTool):
    _appDataDir = "LoadOrderLibrary"
    _apiToken = None
    _slug = None
    _dataFile = ""

    def __init__(self):
        super().__init__()

    def __tr(self, str_):
        return QCoreApplication.translate(self._name, str_)

    def init(self, organizer=mobase.IOrganizer):
        self._dataFile = (
            hashlib.md5(organizer.basePath().encode()).hexdigest() + "-data.json"
        )
        self.loadData()
        return super().init(organizer)

    def name(self) -> str:
        return "API Settings"

    def master(self):
        return self._name

    def description(self) -> str:
        return self.__tr("Add API Token for uploading as a user.")

    def display(self) -> None:
        self.showMessage()

    def tooltip(self) -> str:
        return "Set the API Token"

    def settings(self) -> List[None]:
        return []

    def displayName(self) -> str:
        return "Load Order Library/API Token"

    def icon(self) -> QIcon:
        return QIcon()

    def showMessage(self) -> None:
        self.loadData()
        msg = QInputDialog()
        msg.setWindowTitle("Set API Token")
        token, done = msg.getText(msg, "API Token", "Token: ")

        if done:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Success!")
            msg.setText("Success! Your API token was removed.")
            if token == "":
                self._apiToken = None
            else:
                self._apiToken = token
                msg.setText("Success! Your API token was added.")
            self.saveData()
            msg.exec_()

    def saveData(self) -> None:
        dir = os.path.join(os.getenv("LOCALAPPDATA"), self._appDataDir)
        file = os.path.join(dir, self._dataFile)
        if not os.path.exists(dir):
            os.mkdir(dir)

        data = {
            "apiToken": self._apiToken,
            "slug": self._slug,
            "basePath": self._organizer.basePath(),
        }
        with open(file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def loadData(self) -> None:
        dir = os.path.join(os.getenv("LOCALAPPDATA"), self._appDataDir)
        file = os.path.join(dir, self._dataFile)
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
