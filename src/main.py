# -*- coding: utf-8 -*-
"""Main module.
"""

import argparse
import logging
import os
from typing import (
    List,
    Union
)

import docker
import docker.errors
from telegram import (
    Bot,
    ParseMode,
    Update
)
import telegram.error
from telegram.ext import (
    CallbackQueryHandler,
    Updater
)

from telecom.command import (
    inline_query_handler,
    register_command,
    register_help_command
)

import cmd_hi
import cmd_info
import cmd_logs
import cmd_pause
import cmd_restart
import cmd_restart_bot
import cmd_start
import cmd_stop
import cmd_unpause


TelegramError = Union[telegram.error.TelegramError,
                      telegram.error.NetworkError]


def error_callback(bot: Bot,
                   update: Update,
                   error: TelegramError) -> None:
    # pylint: disable=line-too-long
    """Custom telegram error callback.

    See `telegram.ext.Dispatcher.add_error_handler`_

    .. _telegram.ext.Dispatcher.add_error_handler: https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.dispatcher.html?highlight=error%20callback#telegram.ext.Dispatcher.add_error_handler
    """
    # pylint: disable=unused-argument
    error_name = error.__class__.__name__
    error_message = str(error)
    try:
        logging.error(
            'User "%s" raised a telegram error %s: %s',
            update.message.from_user.username,
            error_name,
            error_message
        )
        bot.send_message(
            chat_id=update.message.chat_id,
            parse_mode=ParseMode.MARKDOWN,
            reply_to_message_id=update.message.message_id,
            text=f'''❌ *TELEGRAM ERROR* ❌
Last command raised a telegram `{error_name}`: {error_message}'''
        )
    except:  # pylint: disable=bare-except
        pass
    else:
        logging.error(
            'Telegram error %s: %s',
            error_name,
            error_message
        )


def init_docker(server: str) -> docker.DockerClient:
    """Inits the docker client.
    """
    client = docker.DockerClient(base_url=server)
    logging.info("Connected to docker socket %s", server)
    return client


def init_telegram(token: str,
                  authorized_users: List[int],
                  docker_client: docker.DockerClient) -> None:
    """Inits the telegram bot.

    Registers commands, polls.
    """
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(CallbackQueryHandler(inline_query_handler))

    register_help_command(dispatcher)

    register_command(
        dispatcher,
        "hi",
        cmd_hi.Hi,
        authorized_users=authorized_users
    )
    register_command(
        dispatcher,
        "info",
        cmd_info.Info,
        authorized_users=authorized_users,
        defaults={
            "docker_client": docker_client
        }
    )
    register_command(
        dispatcher,
        "logs",
        cmd_logs.Logs,
        authorized_users=authorized_users,
        defaults={
            "docker_client": docker_client
        }
    )
    register_command(
        dispatcher,
        "pause",
        cmd_pause.Pause,
        authorized_users=authorized_users,
        defaults={
            "docker_client": docker_client
        }
    )
    register_command(
        dispatcher,
        "restart",
        cmd_restart.Restart,
        authorized_users=authorized_users,
        defaults={
            "docker_client": docker_client
        }
    )
    register_command(
        dispatcher,
        "restart_bot",
        cmd_restart_bot.RestartBot,
        authorized_users=authorized_users,
        defaults={
            "telegram_updater": updater
        }
    )
    register_command(
        dispatcher,
        "start",
        cmd_start.Start,
        authorized_users=authorized_users,
        defaults={
            "docker_client": docker_client
        }
    )
    register_command(
        dispatcher,
        "stop",
        cmd_stop.Stop,
        authorized_users=authorized_users,
        defaults={
            "docker_client": docker_client
        }
    )
    register_command(
        dispatcher,
        "unpause",
        cmd_unpause.Unpause,
        authorized_users=authorized_users,
        defaults={
            "docker_client": docker_client
        }
    )

    updater.start_polling()
    logging.info("Started bot %s", updater.bot.id)
    updater.idle()


def main():
    """Main function.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--authorized-user",
        action="append",
        default=[],
        dest="authorized_users",
        help="Sets an authorized user; reuse this option to add more "
             "authorized users",
        metavar="USERID",
        type=int)
    parser.add_argument(
        "-s", "--server",
        default="unix:///var/run/docker.sock",
        dest="server",
        help="URL to the docker server",
        metavar="URL")
    parser.add_argument(
        "-t", "--token",
        dest="token",
        help="Telegram bot token",
        metavar="TOKEN")
    arguments = parser.parse_args()

    if not arguments.authorized_users:
        logging.warning("No authorized user set! Use the -a flag")

    docker_client = init_docker(arguments.server)
    init_telegram(arguments.token, arguments.authorized_users, docker_client)


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s] %(message)s',
        level={
            "CRITICAL": logging.CRITICAL,
            "DEBUG": logging.DEBUG,
            "ERROR": logging.ERROR,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING
        }[os.environ.get("LOGGING_LEVEL", "WARNING")])
    try:
        main()
    finally:
        logging.shutdown()
