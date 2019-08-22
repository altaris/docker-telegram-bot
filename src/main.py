"""Main.
"""

import argparse
import logging
import os
from typing import (
    List
)

import docker
import telegram
import telegram.ext

# pylint: disable=wrong-import-order
from commands import (
    load_commands
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
    updater = telegram.ext.Updater(token=token)
    load_commands(updater, docker_client, authorized_users)
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
