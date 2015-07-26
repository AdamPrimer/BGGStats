import time
import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

ENDPOINT = {
    "collection": "/collection",
    "thing": "/thing"
}

class BoardGameGeekApi:
    def __init__(self, url):
        self.url = url

    def top_100(self, limit=100):
        games = []
        for i in xrange(0, limit / 100):
            print "Fetching Page {} of {} of the top games on Board Game Geek".format(
                i+1, limit/100)
            r = requests.get(
                "https://boardgamegeek.com/browse/boardgame/page/{}".format(i+1))
            html = BeautifulSoup(r.content, "html.parser")
            items = html.body.find_all('td', attrs={'class':'collection_objectname'})

            for item in items:
                url = item.find('a')['href']
                _, _, bgg_id, _ = url.split("/")
                games.append(bgg_id)
        return games

    def collection(self, username):
        params = {
            'username': username,
            'subtype': 'boardgame',
            'own': 1,
            'stats': 1,
        }

        r = requests.get(
            "{}/{}".format(self.url, ENDPOINT['collection']),
        params=params)

        while r.status_code == 202:
            print "Board Game Geek has queued your request. Trying again in 5 seconds."
            time.sleep(5)
            r = requests.get(
                "{}/{}".format(self.url, ENDPOINT['collection']),
            params=params)

        root = ET.fromstring(r.content)

        collection = {'username': username, 'games': []}
        for item in root:
            stats = item.find('status')
            game = {
                'bgg_id': int(item.attrib['objectid']),
                'stat_ownd': bool(stats.attrib['own']),
                'stat_pown': bool(stats.attrib['prevowned']),
                'stat_fort': bool(stats.attrib['fortrade']),
                'stat_want': bool(stats.attrib['want']),
                'stat_wtp': bool(stats.attrib['wanttoplay']),
                'stat_wtb': bool(stats.attrib['wanttobuy']),
                'stat_wish': bool(stats.attrib['wishlist']),
                'stat_pre': bool(stats.attrib['preordered']),
                'num_plays': int(item.find('numplays').text),
            }

            user_rating = item.find('stats').find('rating').attrib['value']
            if user_rating != "N/A":
                game['user_rating'] = float(user_rating)

            collection['games'].append(game)

        return collection

    def game(self, bgg_id):
        r = requests.get(
            "{}/{}".format(self.url, ENDPOINT['thing']),
        params={
            'id': bgg_id,
            'stats': 1,
        })

        root = ET.fromstring(r.content)

        fields1 = [
            "thumbnail",
            "image",
            "description"]

        fields2 = [
            "yearpublished",
            "minplayers",
            "maxplayers",
            "playingtime",
            "minplaytime",
            "maxplaytime"]

        game = {
            'bgg_id': bgg_id,
        }
        for item in root:
            game['gametype'] = item.attrib['type']
            for child in item:
                field = child.tag
                if field in fields1:
                    game[field] = child.text

                elif field in fields2:
                    game[field] = child.attrib['value']

                # Get game's primary name
                elif field == "name" and child.attrib['type'] == "primary":
                    game['name'] = child.attrib['value']

                # Get game's weight
                elif field == "statistics":
                    game['weight'] = float(
                        child.find('ratings').find('averageweight').attrib['value'])

                # Get the player count poll
                elif child.tag == "poll" and child.attrib['title'] == "User Suggested Number of Players":
                    game['players_poll'] = {}
                    for results in child:
                        num = results.attrib['numplayers']
                        if num[-1] == "+":
                            num = num[:-1]
                            num = int(num) + 1
                        num = int(num)

                        game['players_poll'][num] = {
                            'best': 0,
                            'recommended': 0,
                            'notrecommended': 0
                        }

                        votes = game['players_poll'][num]

                        for result in results:
                            answer = result.attrib['value'].lower().replace(" ", "")
                            num_votes = int(result.attrib['numvotes'])
                            votes[answer] = num_votes

                        votes['total'] = votes['best'] + votes['recommended'] + votes['notrecommended']
                        if not votes['total']:
                            del game['players_poll'][num]

        return game
