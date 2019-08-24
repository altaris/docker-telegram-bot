IMAGE	= docker-telegram-bot
SUDO   ?= sudo

all: check run

check:
	@mypy src/*.py

docker: docker-run

docker-build:
	$(SUDO) docker build -t $(IMAGE):$$(git rev-parse --abbrev-ref HEAD) .

.ONESHELL:
docker-run: build-docker
	@. ./secret.env
	@$(SUDO) docker run --rm									\
		--env "LOGGING_LEVEL=$${LOGGING_LEVEL:-WARNING}"		\
		--name $(IMAGE)-test									\
		--volume /var/run/docker.sock:/var/run/docker.sock 		\
		$(IMAGE):$$(git rev-parse --abbrev-ref HEAD)			\
		-a "$${TELEGRAM_ADMIN}" -t "$${TELEGRAM_TOKEN}"

.ONESHELL:
run:
	@$(SUDO) -E -s . ./venv/bin/activate 	&& \
		. ./secret.env 						&& \
		python3 src/main.py -a $${TELEGRAM_ADMIN} -t $${TELEGRAM_TOKEN}
