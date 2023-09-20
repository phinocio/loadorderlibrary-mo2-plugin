import mobase

from typing import List

from .upload import LolMo2Upload

try:
    from PyQt5.QtWidgets import QMessageBox, QInputDialog
    from PyQt5.QtGui import QIcon
except:
    from PyQt6.QtWidgets import QMessageBox, QInputDialog
    from PyQt6.QtGui import QIcon


class LolMo2Slug(LolMo2Upload, mobase.IPluginTool):
    def __init__(self):
        super().__init__()

    def init(self, organizer=mobase.IOrganizer):
        self.loadData()
        return super().init(organizer)

    def name(self) -> str:
        return "Set Slug"

    def master(self):
        return self._name

    def description(self) -> str:
        return self.tr("Add slug to manage.")

    def display(self) -> None:
        self.showMessage()

    def tooltip(self) -> str:
        return "Set the list's slug"

    def settings(self) -> List[None]:
        return []

    def displayName(self) -> str:
        return "Load Order Library/Set Slug"

    def icon(self) -> QIcon:
        return QIcon()

    def showMessage(self) -> None:
        self.loadData()
        msg = QInputDialog()
        msg.setWindowTitle("Set Slug")
        slug, done = msg.getText(msg, "Slug", "Slug: ")

        if done:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("Success!")
            if slug == "":
                self._slug = None
                msg.setText("Success! Your slug was removed.")
            else:
                self._slug = slug
                msg.setText(
                    f"Success! Your slug was added. Now managing <b>{self._slug}</b>."
                )
            self.saveData()
            msg.exec()
