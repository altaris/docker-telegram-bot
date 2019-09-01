# -*- coding: utf-8 -*-
"""Implentation of command `/hi`.
"""

from telegram import (
    ReplyKeyboardMarkup
)

from docker_utils import (
    DockerCommand
)


COMMAND_KEYBOARD: ReplyKeyboardMarkup = ReplyKeyboardMarkup([
    ["/info", "/logs", "/help"],
    ["/start", "/stop", "/restart"],
    ["/pause", "/unpause"],
    ["/restart_bot"]
])


class Hi(DockerCommand):
    """Implementation of command `/hi`.
    """

    def main(self) -> None:
        self.reply(
            f'Hi {self._message.from_user.first_name} 👋 I am your personal '
            f'docker assistant. Please choose a command.',
            reply_markup=COMMAND_KEYBOARD
        )
