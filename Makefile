# Makefile

CC = gcc
CFLAGS = -fPIC -Wall -Werror
LIB = build/libmath.so

.PHONY: all test robot clean

all: $(LIB)

$(LIB): math.c
	@mkdir -p build
	$(CC) $(CFLAGS) -shared -o $(LIB) math.c

robot: all
	robot robot

unit_test: all
	pytest tests

system_test: all
	robot tests/system

lint:
	ruff check .
	black --check .

format:
	black .

clean:
	rm -rf build
	find . -type f -name "*.pyc" -delete

.PHONY: help
help:
	@echo "Makefile commands:"
	@echo "  all          - Build the shared library"
	@echo "  unit_test    - Run unit tests with pytest"
	@echo "  system_test  - Run system tests with Robot Framework"
	@echo "  lint         - Check code style with ruff and black"
	@echo "  format       - Format code with black"
	@echo "  clean        - Clean build artifacts and Python bytecode"
