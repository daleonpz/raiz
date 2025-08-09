# Makefile

CC = gcc
CFLAGS = -fPIC -Wall -Werror
LIB = build/libmath.so

.PHONY: all robot clean

all: $(LIB)

$(LIB): math.c
	@mkdir -p build
	$(CC) $(CFLAGS) -shared -o $(LIB) math.c

robot: all
	robot robot

clean:
	rm -rf build
	find . -type f -name "*.pyc" -delete

.PHONY: help
help:
	@echo "Makefile commands:"
	@echo "  all          - Build the shared library"
	@echo "  robot        - Run the robot tests"
	@echo "  clean        - Clean build artifacts"
