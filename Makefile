IMAGE			 = docker-telegram-bot
LOGGING_LEVEL	?= WARNING
SECRET_ENV		 = ./secret.env
SUDO   			?= sudo
VENV_ACTIVATE	 = ./venv/bin/activate

all: check run

check:
	mypy src/telecom/*.py
	mypy src/*.py

clean:
	rm -rf build/

.ONESHELL:
doc:
	. $(VENV_ACTIVATE)
	pip install -U sphinx sphinxcontrib-napoleon
	sphinx-build -b html sphinx/ build/
	-xdg-open build/index.html

docker: docker-run

docker-build: check
	$(SUDO) docker build -t $(IMAGE):$$(git rev-parse --abbrev-ref HEAD) .

.ONESHELL:
docker-run: docker-build
	@echo Running $(IMAGE):$$(git rev-parse --abbrev-ref HEAD)
	@$(SUDO) docker run --rm								\
		--env "LOGGING_LEVEL=$(LOGGING_LEVEL)"				\
		--env-file $(SECRET_ENV)							\
		--name $(IMAGE)-test								\
		--volume /var/run/docker.sock:/var/run/docker.sock 	\
		$(IMAGE):$$(git rev-parse --abbrev-ref HEAD)

.ONESHELL:
run:
	@echo Running python3 src/main.py
	@$(SUDO) -- sh -c '										\
		. $(VENV_ACTIVATE); 								\
		. $(SECRET_ENV); 									\
		LOGGING_LEVEL=$(LOGGING_LEVEL) python3 src/main.py 	\
			-a $${TELEGRAM_ADMIN} -t $${TELEGRAM_TOKEN}		\
	'
