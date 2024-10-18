#!/bin/bash

if [ "$(uname)" == "Linux" ]; then
	if [ ! -d "/home/${USER}/data" ]; then
		mkdir -p ~/data/db-volume
		mkdir -p ~/data/user-db
		mkdir -p ~/data/media
	fi
elif [ "$(uname)" == "Darwin" ]; then
	if [ ! -d "/Users/${USER}/data" ]; then
		mkdir -p ~/data/db-volume
		mkdir -p ~/data/user-db
		mkdir -p ~/data/media
	fi
fi