
all: chech run

check:
	@mypy src/*.py

run:
	@sudo ./run.sh
