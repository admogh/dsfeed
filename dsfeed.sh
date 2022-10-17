#!/bin/sh

SCRIPT_DIR=$(cd $(dirname $0); pwd)
echo "SCRIPT_DIR:$SCRIPT_DIR"
source $SCRIPT_DIR/.env

kill_chrome () {
    killall chromedriver
    killall chrome
}

execpy () {
    kill_chrome
		if [ -n "$PYTHON_BIN_PATH" ]; then
			$PYTHON_BIN_PATH -u ${SCRIPT_DIR}/${1}.py
		else
			python -u ${SCRIPT_DIR}/${1}.py
		fi
    kill_chrome
}

execpy main
