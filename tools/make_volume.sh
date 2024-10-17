#!/bin/bash

if [ "$(uname)" == "Linux" ]; then
	if [ ! -d "/home/${USER}/data" ]; then
		mkdir -p ~/data/db-volume
		mkdir -p ~/data/user-db
	fi
	if [ ! -d "/home/${USER}/user-db" ]; then
		mkdir -p ~/data/user-db
	fi
elif [ "$(uname)" == "Darwin" ]; then
	if [ ! -d "/Users/${USER}/data" ]; then
		mkdir -p ~/data/db-volume
	fi
	if [ ! -d "/home/${USER}/user-db" ]; then
		mkdir -p ~/data/user-db
	fi
fi