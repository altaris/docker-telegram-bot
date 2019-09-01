# -*- coding: utf-8 -*-
"""Implentation of command `/restart_bot`.
"""

import logging
import os
import sys
from threading import (
    Thread
)

from telegram.ext import (
    Updater
)

from telecom.command import (
    Command
)
from telecom.selector import (
    YesNoSelector
)

class RestartBot(Command):
    """Implementation of command `/restart_bot`.
    """

    __HELP__ = """▪️ Usage: `/restart_bot`:
Restarts this bot."""

    def main(self):

        def target():
            self.updater.stop()
            os.execl(sys.executable, sys.executable, *sys.argv)

        confirmation = self.arg(
            "confirmation",
            YesNoSelector(),
            "This will restart the current telegram bot. Are you sure?"
        )
        if confirmation:
            self.reply("🔄 Bot restarting...")
            logging.info("Bot restarting...")
            Thread(target=target).start()


    @property
    def updater(self) -> Updater:
        """Returns the ``telegram.ext.updater`` of this command.
        """
        updater = self._args_dict.get("telegram_updater", None)
        if not isinstance(updater, Updater):
            raise ValueError(
                'Instances of RestartBot must have a telegram updater as '
                'default value for key "telegram_updater"'
            )
        return updater
