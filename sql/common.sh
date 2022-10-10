#!/bin/sh

function insert_source () {
  DIR="$( cd "$( dirname "$0" )" && pwd -P )"
  DT=`date '+%Y-%m-%d %H:%M:%S'`
	if [ -z "$2" ]; then
    KEYWORD=$1
  else
    KEYWORD=$2
  fi
  SQL='insert into sources (url, keyword, created, updated) values ("'$1'", "'$KEYWORD'", "'$DT'", "'$DT'");'
  echo "SQL:"$SQL
  echo "dsfee.db:"$DIR"/../dsfeed.db"
  sqlite3 $DIR/../dsfeed.db "$SQL"
}
