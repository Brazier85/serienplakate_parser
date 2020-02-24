import requests, datetime, argparse
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

class Parser:
    def __init__(self):
        remote_page = requests.get(BASE_URL, stream=True)
        self.page = BeautifulSoup(remote_page.content, 'html.parser')
    
    def get_poster_ids(self):
        # Suche alle vorhandenen Serien
        content = self.page.find('div', attrs={'class':'categorie-content'})
        posters = content.findAll('div', attrs={'class': 'item'})
        return [x.attrs['data-sid'] for x in posters]

    def check_poster_availability(self, poster_id) -> int:
        # Suche ob es für die Serie Poster gibt
        response = requests.post('{}backend/_ajax.php'.format(BASE_URL),
            data={'cmd': 'poster', 'sId': poster_id}
        )

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.send_telegram_message(message='{} errored:{}'.format(BASE_URL, e))
            raise

        try:
            html = BeautifulSoup(response.json()['data'], 'html.parser')
        except:
            self.send_telegram_message('ParserError while checking poster {}'.format(poster_id))
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
        bot.send_message(chat_id=TELEGRAM_USER_ID, text=message)

    def run(self):
        poster_ids = self.get_poster_ids()
        order_available = any([self.check_poster_availability(pid) > 0 for pid in poster_ids])
        if order_available:
            message = 'I found a free poster to order at {}'.format(BASE_URL)
            self.send_telegram_message(message=message)
        else:
            now = datetime.datetime.now()
            print(now.strftime("%d:%m:%Y %H:%M:%S") + " nothing found!")
            #self.send_telegram_message(message="test")
        return order_available


if __name__ == '__main__':
    parser = Parser()
    parser.run()
