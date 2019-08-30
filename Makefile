IMAGE	= docker-telegram-bot
SUDO   ?= sudo

LOGGING_LEVEL	?= WARNING

all: check run

check:
	@mypy src/*.py

docker: docker-run

docker-build:
	$(SUDO) docker build -t $(IMAGE):$$(git rev-parse --abbrev-ref HEAD) .

.ONESHELL:
docker-run: docker-build
	@. ./secret.env
	@$(SUDO) docker run --rm									\
		--env "LOGGING_LEVEL=$${LOGGING_LEVEL:-WARNING}"		\
		--env-file secret.env									\
		--name $(IMAGE)-test									\
		--volume /var/run/docker.sock:/var/run/docker.sock 		\
		$(IMAGE):$$(git rev-parse --abbrev-ref HEAD)

.ONESHELL:
run:
	@$(SUDO) -- sh -c '											\
		. ./venv/bin/activate; 									\
		. ./secret.env; 										\
		LOGGING_LEVEL=$(LOGGING_LEVEL) python3 src/main.py 		\
			-a $${TELEGRAM_ADMIN} -t $${TELEGRAM_TOKEN}			\
	'
