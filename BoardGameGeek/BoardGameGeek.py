from BoardGameGeekApi import BoardGameGeekApi
from BoardGameGeekDb import BoardGameGeekDb
from collections import defaultdict

PATH = {
    "api": "https://www.boardgamegeek.com/xmlapi2",
    "db": "sqlite:///cache.db"
}

class BoardGameGeek():
    def __init__(self, api_url=PATH['api'], db_path=PATH['db']):
        self.api = BoardGameGeekApi(url=api_url)
        self.db = BoardGameGeekDb(path=db_path)

    def get_collection(self, username, refresh=False, include_xpac=False):
        return BoardGameGeekCollection(self.api, self.db, username, refresh, include_xpac)

    def get_game(self, bgg_id):
        return BoardGameGeekGame(self.api, self.db, bgg_id)

    def top_100(self, limit=100, include_xpac=True):
        top100 = self.api.top_100(limit=limit)
        games = []
        for i, bgg_id in enumerate(top100):
            if not self.db.has_game(bgg_id):
                print "Fetching Game {} of {}".format(i+1, len(top100))
            game = BoardGameGeekGame(self.api, self.db, bgg_id)
            game.data['user_rating'] = 'N/A'
            if include_xpac or game['gametype'] == "boardgame":
                games.append(game)
        return games

    def search(self, query, retall=False):
        results = self.api.search(query=query)

        exact = [x for x in results if x['name'] == query]

        if not retall and len(exact) == 1:
            return BoardGameGeekGame(self.api, self.db, exact[0]['bgg_id'])
        elif not retall and len(exact) > 1:
            games = []
            for i, g in enumerate(exact):
                game = BoardGameGeekGame(self.api, self.db, g['bgg_id'])
                game.data['user_rating'] = g.get('user_rating', 'N/A')
                games.append(game)
            return games
        else:
            games = []
            for i, g in enumerate(results):
                game = BoardGameGeekGame(self.api, self.db, g['bgg_id'])
                game.data['user_rating'] = g.get('user_rating', 'N/A')
                games.append(game)
            return games

class BoardGameGeekCollection:
    def __init__(self, api, db, username, refresh=False, include_xpac=False):
        self.api = api
        self.db = db

        self.username = username
        self.refresh = refresh
        self.include_xpac = include_xpac
        self.games = self._get()

    def _get(self):
        c = self.db.collection(self.username)
        if not c or self.refresh:
            c = self.api.collection(self.username)
            self.db.collection_add(c)
            self.refresh = False

        games = []
        for i, g in enumerate(c['games']):
            if not self.db.has_game(g['bgg_id']):
                print "Fetching {} of {}".format(i+1, len(c['games']))
            game = BoardGameGeekGame(self.api, self.db, g['bgg_id'])
            game.data['user_rating'] = g.get('user_rating', 'N/A')
            if self.include_xpac or game['gametype'] == "boardgame":
                games.append(game)

        return games

    def good_at(self, num_players, neg_thresh=0.2, pos_thresh=0.4):
        '''Determine games that are good to play at a certain player count based
        on the votes of players on the website Board Game Geek.

        Takes into account a maximum number of "Not Recommended" votes, and a
        minimum number of required "Best" votes before a recommendation is
        made.'''

        good_at = []
        for game in self:
            if num_players not in game['players_poll'].keys():
                continue

            ans = game['players_poll'][num_players]
            total = float(ans['total'])
            if (not total or
                    ans['notrecommended'] / total > neg_thresh or
                    ans['best'] / total < pos_thresh):
                continue

            good_at.append(game)

        return good_at

    def best_at(self, num_players=0):
        '''Determine which player count is voted the 'best' by players from the
        website Board Game Geek.'''

        best_at = defaultdict(list)

        for game in self:
            current_best = (0, 0)
            poll = game['players_poll']
            for num, ans in poll.iteritems():
                total = float(ans['total'])
                if not total:
                    continue

                if ans['best'] / total > current_best[1]:
                    current_best = (num, ans['best'] / total)

            best_at[current_best[0]].append(game)

        if not num_players:
            return sorted(best_at.items(), key=lambda x: x[0])
        else:
            return best_at.get(num_players, [])

    def __getitem__(self, key):
        return self.games[key]

    def __iter__(self):
        for x in self.games:
            yield x

    def __str__(self):
        return "{}: {}".format(
            self.username, str([x for x in self.games]))

class BoardGameGeekGame:
    def __init__(self, api, db, bgg_id):
        self.api = api
        self.db = db

        self.bgg_id = bgg_id
        self.data = self._get()

    def __getitem__(self, key):
        if key == "bgg_id":
            return self.bgg_id
        else:
            return self.data[key]

    def _get(self):
        data = self.db.game(self.bgg_id)
        if not data:
            data = self.api.game(self.bgg_id)
            self.db.game_add(data)
        return data

    def __str__(self):
        return self['name']
