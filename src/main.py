"""Main.
"""

import argparse
import functools
import logging
import os
from typing import (
    List,
    Union
)

import docker
import telegram

# pylint: disable=wrong-import-order
import commands


TelegramError = Union[telegram.error.TelegramError,
                      telegram.error.NetworkError]


def error_callback(bot: telegram.Bot,
                   update: telegram.Update,
                   error: TelegramError) -> None:
    # pylint: disable=line-too-long
    """Custom telegram error callback.

    See https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.dispatcher.html?highlight=error%20callback#telegram.ext.Dispatcher.add_error_handler
    """
    # pylint: disable=unused-argument
    try:
        raise error
    except telegram.error.Unauthorized:
        logging.error("Unauthorized")
    except telegram.error.BadRequest:
        logging.error("BadRequest")
    except telegram.error.TimedOut:
        logging.error("TimedOut")
    except telegram.error.NetworkError:
        logging.error("NetworkError")
    except telegram.error.ChatMigrated:
        logging.error("ChatMigrated")
    except telegram.error.TelegramError:
        logging.error("TelegramError")


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
    updater = telegram.ext.Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error_callback)
    for k in commands.COMMANDS:
        logging.debug("Registering command %s", k)
        dispatcher.add_handler(telegram.ext.CommandHandler(
            k,
            functools.partial(commands.COMMANDS[k], docker_client),
            filters=telegram.ext.filters.Filters.user(authorized_users),
            pass_args=True))
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
        type="int")
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
    (options, _) = parser.parse_args()

    if not options.authorized_users:
        logging.warning("No authorized user set! Use the -a flag")

    docker_client = init_docker(options.server)
    init_telegram(options.token, options.authorized_users, docker_client)


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
