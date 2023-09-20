import mobase
import os
import json
import hashlib

from typing import List

from .upload import LolMo2Upload

try:
    from PyQt5.QtCore import QCoreApplication
    from PyQt5.QtWidgets import QMessageBox, QInputDialog
    from PyQt5.QtGui import QIcon
except:
    from PyQt6.QtCore import QCoreApplication
    from PyQt6.QtWidgets import QMessageBox, QInputDialog
    from PyQt6.QtGui import QIcon


class LolMo2ApiToken(LolMo2Upload, mobase.IPluginTool):
    def __init__(self):
        super().__init__()

    def init(self, organizer=mobase.IOrganizer):
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
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success!")
            msg.setText("Success! Your API token was removed.")
            if token == "":
                self._apiToken = None
            else:
                self._apiToken = token
                msg.setText("Success! Your API token was added.")
            self.saveData()
            msg.exec()
