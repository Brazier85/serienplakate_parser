# Parser for http://serienplakate.de/

[serienplakate](http://serienplakate.de/) provides free limited posters for every new Netflix show.
This script based on [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) parses website and notifies me via [Telegram](https://core.telegram.org/) if there are posters available to order.

The original script is from [amureki](https://github.com/amureki/serienplakate_parser)

## Setup
Install the requestet packages via pip. You can find them in the file named `Pipfile`. To run the script you just have to add your bot-token and your chatid to the script as arguments:

```main.py TOKEN CHAT```

## Crontab

Scrapes the website once a hour and searches for new poster

```
0 * * * *  /usr/bin/python3 /data/python/serienplakate/main.py TOKEN CHAT > /root/plakate.log 2>&1
```
