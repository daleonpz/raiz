# Makefile

CC = gcc
CFLAGS = -fPIC -Wall -Werror
LIB = build/libmath.so

.PHONY: all test robot clean

all: $(LIB)

$(LIB): math.c
	@mkdir -p build
	$(CC) $(CFLAGS) -shared -o $(LIB) math.c

test: all
	pytest tests

robot: all
	robot robot/test_math.robot

lint:
	ruff check .
	black --check .

format:
	black .

clean:
	rm -rf build
	find . -type f -name "*.pyc" -delete

