# Don't stop feed - for sustainable and portable feed

Dsfeed is Python script to get sustainable feed.  
The feeds means not only RSS and Atom but also just a site with updated links.  
Assumed serverless and using ChromeDriver and sqlite.

## Usages
###  Get specific site feed
```sh
$ python -u main.py https://news.google.com/
$ python -u main.py https://news.google.com/rss
```

### From DB
```sh
$ ./sql/sources.sh https://news.google.com/ https://www.afpbb.com/
$ ./sql/source.sh https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB news-google-entertainment
$ sqlite3 ./dsfeed.db 
SQLite version 3.28.0 2019-04-16 19:49:53
Enter ".help" for usage hints.
sqlite> select * from sources;
5|https://news.google.com/|https://news.google.com/|2022-10-10 15:21:43|2022-10-10 15:21:43
6|https://www.afpbb.com/|https://www.afpbb.com/|2022-10-10 15:21:43|2022-10-10 15:21:43
7|https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNREpxYW5RU0FtVnVHZ0pWVXlnQVAB|news-google-entertainment|2022-10-10 15:21:49|2022-10-10 15:21:49
sqlite> .quit
```

```sh
$ python -u main.py
```

## Setup 
* create and set .env
```
$ cat .env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/.../...
```

* crontab example
```
0 */2 * * *		/Users/admogh/src/dsfeed/dsfeed.sh > /Users/admogh/log/dsfeed_$( date '+\%Y\%m\%d\%H\%M\%S' ).log 2>&1
```


