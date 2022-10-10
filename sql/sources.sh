#!/bin/sh

DIR="$( cd "$( dirname "$0" )" && pwd -P )"
. $DIR/common.sh

for ARG in "$@"; do
  echo "ARG:$ARG"
  insert_source $ARG
done
