#!/usr/bin/env python3

import requests, datetime, argparse, datetime
from bs4 import BeautifulSoup
from telegram import Bot

# Register arguments and parse them
argsp = argparse.ArgumentParser()
argsp.add_argument("token")
argsp.add_argument("chat")
args = argsp.parse_args()

BASE_URL = 'https://serienplakate.de/'
TELEGRAM_BOT_TOKEN = args.token
TELEGRAM_USER_ID = args.chat
HEADER = "[SERIENPLAKATE.DE]\n\n"

class Parser:
    def __init__(self):
        remote_page = requests.get(BASE_URL, stream=True)
        self.page = BeautifulSoup(remote_page.content, 'html.parser')
        # Heartbeat
        now = datetime.datetime.now()
        if now.hour == 12:
            self.send_telegram_message(message="Script is still running")        
        # Maintainance detection
        if "gewartet" in self.page.title.string:
            if (now.hour == 12):
                self.send_telegram_message(message="Maintainance mode detected")
            print("Page is in maintainance mode!")
            exit(1)
        if "401" in self.page.title.string:
            if (now.hour == 12):
                self.send_telegram_message(message="Page needs login \(*401 found*\)")
            print("Page needs login (401 found)")
            exit(1)
    
    def get_poster_data(self):
        # Suche alle vorhandenen Serien
        content = self.page.find('div', attrs={'class':'categorie-content'})
        try:
            posters = content.findAll('div', attrs={'class': 'item'})
        except Exception as ex:
            self.send_telegram_message(message="Error in function *get\_poster\_id*:\n\n{}".format(ex))
            raise

        d = dict();

        for x in posters:
            sId = x.attrs['data-sid']
            sName = x.attrs['data-sname']
            d[sId] = sName

        print(d)
        return d

    def check_poster_availability(self, poster_id, poster_name) -> int:
        # Suche ob es für die Serie Poster gibt
        response = requests.post('https://www2.serienplakate.de/backend/_ajax.php',
            data={'cmd': 'poster', 'sId': poster_id, 'sName': poster_name, 'selected': poster_id}
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.send_telegram_message(message='Error in function *check_poster_availability*:\n\n{}'.format(e))
            raise

        try:
            html = BeautifulSoup(response.json()['data'], 'html.parser')
        except Exception as ex:
            self.send_telegram_message(message='Error in function *check_poster_availability* with posterid *{}*:\n\n{}'.format(poster_id, ex))
            return 0
        quantity_block = html.findAll('div', attrs={'class': 'count'})
        quantity_proportion = [x.text for x in quantity_block]
        quantity_available = [x.split('/')[0] for x in quantity_proportion]

        for x in quantity_available:
            x = int(x)
            if (x > 0):
                return x
        
        return 0

    def send_telegram_message(self, message):
        bot = Bot(TELEGRAM_BOT_TOKEN)
        message = HEADER + message
        message = message.replace(".", "\.").replace(")","\)").replace("(","\(").replace("_","\_")
        bot.send_message(chat_id=TELEGRAM_USER_ID, text=message, parse_mode="MarkdownV2")

    def run(self):
        poster_ids = self.get_poster_data()
        print(len(poster_ids))
        order_available = any([self.check_poster_availability(poster_id, poster_ids[poster_id]) > 0 for poster_id in poster_ids])
        if order_available:
            message = 'I found a free poster to order at [link]{}'.format(BASE_URL)
            self.send_telegram_message(message=message)
        else:
            now = datetime.datetime.now()
            print(now.strftime("%d:%m:%Y %H:%M:%S") + " nothing found!")
            #self.send_telegram_message(message="test")
        return order_available


if __name__ == '__main__':
    parser = Parser()
    parser.run()
