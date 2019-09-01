docker-telegram-bot
===================

[![Docker Build Status](https://img.shields.io/docker/cloud/build/altaris/docker-telegram-bot)](https://hub.docker.com/r/altaris/docker-telegram-bot/)
[![Maintainability](https://api.codeclimate.com/v1/badges/ca764082909cf0056c51/maintainability)](https://codeclimate.com/github/altaris/docker-telegram-bot/maintainability)
[![Docs](https://img.shields.io/badge/docs-over%20here-success)](https://altaris.github.io/docker-telegram-bot/index.html)
![Python 3](https://badgen.net/badge/Python/3/blue)
[![MIT License](https://badgen.net/badge/license/MIT/blue)](https://choosealicense.com/licenses/mit/)

This telegram bot allows you to manage your docker deamon.

1. [Create a telegram bot](https://telegram.me/botfather);
2. Copy a `secret.env` from the `secret.env.template` template;
3. Run
```sh
# To run in shell
make run
# To run in docker
make docker-run
```
4. Say `/hi` to the bot to get started.
