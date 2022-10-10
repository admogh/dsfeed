#!/bin/sh

SCRIPT_DIR=$(cd $(dirname $0); pwd)
echo "SCRIPT_DIR:$SCRIPT_DIR"

kill_chrome () {
    killall chromedriver
    killall chrome
}

execpy () {
    kill_chrome
    python -u ${SCRIPT_DIR}/${1}.py
    kill_chrome
}

execpy main
