"""Main.
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
    SimpleCommand
)


TelegramError = Union[telegram.error.TelegramError,
                      telegram.error.NetworkError]


def error_callback(bot: Bot,
                   update: Update,
                   error: TelegramError) -> None:
    # pylint: disable=line-too-long
    """Custom telegram error callback.

    See https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.dispatcher.html?highlight=error%20callback#telegram.ext.Dispatcher.add_error_handler
    """
    # pylint: disable=unused-argument
    try:
        raise error
    except telegram.error.Unauthorized as err:
        logging.error("Unauthorized: %s", str(err))
    except telegram.error.BadRequest as err:
        logging.error("BadRequest: %s", str(err))
    except telegram.error.TimedOut as err:
        logging.error("TimedOut: %s", str(err))
    except telegram.error.NetworkError as err:
        logging.error("NetworkError: %s", str(err))
    except telegram.error.ChatMigrated as err:
        logging.error("ChatMigrated: %s", str(err))
    except telegram.error.TelegramError as err:
        logging.error("TelegramError: %s", str(err))



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
    register_command(
        dispatcher,
        "test",
        SimpleCommand,
        authorized_users=authorized_users
    )
    updater.start_polling()
    logging.info("Started bot %s", updater.bot.id)


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
