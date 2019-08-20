from docker import DockerClient
from functools import partial
import logging
import optparse
import os
from telegram import Bot, Update
import telegram.error
from telegram.ext import CommandHandler, Updater
from telegram.ext.filters import Filters
from typing import Callable, Dict, List, Optional, Union

import commands


TelegramError = Union[telegram.error.TelegramError,
                      telegram.error.NetworkError]


def error_callback(bot: Bot,
                   update: Update,
                   error: TelegramError) -> None:
    """Custom telegram error callback.

    See https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.dispatcher.html?highlight=error%20callback#telegram.ext.Dispatcher.add_error_handler
    """
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


def init_docker(server: str) -> DockerClient:
    """Inits the docker client.
    """
    client = DockerClient(base_url=server)
    logging.info("Connected to docker socket {}".format(server))
    return client


def init_telegram(token: str,
                  authorized_users: List[int],
                  docker_client: DockerClient) -> None:
    """Inits the telegram bot.

    Registers commands, polls.
    """
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error_callback)
    for k in commands.commands:
        dispatcher.add_handler(CommandHandler(
            k,
            partial(commands.commands[k], docker_client),
            filters=Filters.user(authorized_users),
            pass_args=True))
    updater.start_polling()
    logging.info("Started bot {}".format(updater.bot.id))


def main():
    """Main function.
    """
    parser = optparse.OptionParser()
    parser.add_option(
        "-a", "--authorized-user",
        action="append",
        default=[],
        dest="authorized_users",
        help="Sets an authorized user; reuse this option to add more "
             "authorized users",
        metavar="USERID",
        type="int")
    parser.add_option(
        "-s", "--server",
        default="unix:///var/run/docker.sock",
        dest="server",
        help="URL to the docker server",
        metavar="URL")
    parser.add_option(
        "-t", "--token",
        dest="token",
        help="Telegram bot token",
        metavar="TOKEN")
    (options, args) = parser.parse_args()

    if len(options.authorized_users) == 0:
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
