
all: chech run

check:
	@mypy src/*.py

run:
	@sudo -E ./run.sh
