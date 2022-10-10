#!/bin/sh

DIR="$( cd "$( dirname "$0" )" && pwd -P )"
. $DIR/common.sh

echo "url:$1, keyword:$2"
insert_source $1 $2
