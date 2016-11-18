SHELL := /bin/bash

all: src/gravi_utils.c

	gcc -std=gnu9x -pedantic -Wall -Wextra src/gravi_utils.c -o gravi_utils

install:
	cp gravi_utils /usr/local/bin

docs:
	doxygen src/gravi_utils.c

uninstall:
	rm /usr/local/bin/gravi_utils
