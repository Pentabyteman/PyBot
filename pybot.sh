#!/usr/bin/env bash

#This is a command line tool for linux systems only!

DIR=$(find /home -name 'client' -print -quit)
cd $DIR
python3 client.py