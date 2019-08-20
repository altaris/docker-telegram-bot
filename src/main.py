from docker import DockerClient
from functools import partial
import json
import logging
import optparse
import telegram
from telegram import Bot
import telegram.error
import telegram.ext
from telegram.ext import Updater
from typing import Callable, Dict, List, Optional

Command = Callable[[DockerClient, Bot, Updater, List[str]], None]

authorized_users = []  # type: List[int]
commands = {}  # type: Dict[str, Command]


def command(name: Optional[str] = None):
    def decorator(callback: Command):
        def wrapper(client: DockerClient,
                    bot: Bot,
                    update: Updater,
                    args: List[str]) -> None:
            if update.message.from_user.id not in authorized_users:
                bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Hello {}. Unfortonately, you do *not* seem to be an "
                         "authorized user. *I will therefore not accept any "
                         "command you issue.*"
                         .format(update.message.from_user.first_name),
                         parse_mode=telegram.ParseMode.MARKDOWN)
            elif len(args) > 0 and args[0] == "help":
                if callback.__doc__ == '':
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text="No help for command {}".format(name),
                        parse_mode=telegram.ParseMode.MARKDOWN)
                else:
                    bot.send_message(
                        chat_id=update.message.chat_id,
                        text="*Help for command `{}`*\n{}".format(
                            name, callback.__doc__),
                        parse_mode=telegram.ParseMode.MARKDOWN)
            else:
                return callback(client, bot, update, args)
        if name:
            global commands
            commands[name] = wrapper
        return wrapper
    return decorator


@command("start")
def command_start(client: DockerClient,
                  bot: Bot,
                  update: Updater,
                  args: List[str]) -> None:
    """Reinitialize the bot's internal state for that user."""
    bot.send_message(
        chat_id=update.message.chat_id,
        reply_markup=telegram.ReplyKeyboardMarkup(
            [
                [
                    "/info"
                ]
            ]
        ),
        text="Hello {} 👋 I am you docker assistant. Please select a command."
             .format(update.message.from_user.first_name))


@command("info")
def command_info(client: DockerClient,
                 bot: Bot,
                 update: Updater,
                 args: List[str]) -> None:
    """Provides global informations about the current docker daemon."""
    info = client.info()
    reply = f'''▪️ Docker version: {info["ServerVersion"]}
▪️ Memory: {info["MemTotal"]}
▪️ Running containers: {info["ContainersRunning"]}
▪️ Paused containers: {info["ContainersPaused"]}
▪️ Stopped containers: {info["ContainersStopped"]}'''
    bot.send_message(chat_id=update.message.chat_id, text=reply)


def error_callback(bot, update, error):
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


def main():
    parser = optparse.OptionParser()
    parser.add_option("-a", "--authorized-user", action="append",
                      dest="authorized_users",
                      help="Sets an authorized user; reuse this option to add "
                           "more authorized users",
                      metavar="USERID", type="int")
    parser.add_option("-s", "--server", default="unix:///var/run/docker.sock",
                      dest="server", help="URL to the docker server",
                      metavar="URL")
    parser.add_option("-t", "--token", dest="token",
                      help="Telegram bot token", metavar="TOKEN")
    (options, args) = parser.parse_args()

    if not options.authorized_users:
        logging.warning("No authorized user set! Use the -a flag")
    else:
        global authorized_users
        authorized_users = options.authorized_users

    global docker_client
    docker_client = DockerClient(base_url=options.server)
    logging.info("Connected to docker socket {}".format(options.server))

    updater = Updater(token=options.token)
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error_callback)
    for k in commands:
        dispatcher.add_handler(
            telegram.ext.CommandHandler(
                k, partial(commands[k], docker_client), pass_args=True))
    updater.start_polling()
    logging.info("Started bot {}".format(updater.bot.id))


if __name__ == "__main__":
    logging.basicConfig(
        format='[%(levelname)s] %(asctime)s %(name)s: %(message)s',
        level=logging.INFO)
    try:
        main()
    finally:
        logging.shutdown()
