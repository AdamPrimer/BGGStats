from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc
from BoardGameGeekDbSchema import Base, Game, GamePlayerPoll, GameCollection

class BoardGameGeekDb:
    def __init__(self, path):
        engine = create_engine(path)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.db = DBSession()

    def game(self, bgg_id):
        try:
            c = self.db.query(Game).filter(
                Game.bgg_id == bgg_id).one()
        except exc.NoResultFound:
            return False

        p = self.db.query(GamePlayerPoll).filter(
            GamePlayerPoll.bgg_id == bgg_id).all()

        game = {
            'bgg_id': bgg_id,
            'name': c.name,
            'gametype': c.gametype,
            'description': c.description,
            'yearpublished': c.year,
            'image': c.image,
            'thumbnail': c.thumbnail,
            'minplayers': c.play_min,
            'maxplayers': c.play_max,
            'playingime': c.time_avg,
            'minplaytime': c.time_min,
            'maxplaytime': c.time_max,
            'weight': c.weight,
            'players_poll': {},
        }

        for item in p:
            game['players_poll'][item.player_count] = {
                'best': item.best,
                'recommended': item.recc,
                'notrecommended': item.nrec,
                'total': item.total,
            }

        return game

    def game_add(self, game):
        item = Game(
            bgg_id = game['bgg_id'],
            name = game['name'],
            description = game.get('description', ''),
            year = game.get('yearpublished', 0),
            image = game.get('image', ''),
            thumbnail = game.get('thumbnail', ''),
            play_min = game['minplayers'],
            play_max = game['maxplayers'],
            time_avg = game['playingtime'],
            time_min = game['minplaytime'],
            time_max = game['maxplaytime'],
            gametype = game['gametype'],
            weight = game['weight'],
        )
        self.db.add(item)

        for count, votes in game['players_poll'].iteritems():
            poll = GamePlayerPoll(
                bgg_id = game['bgg_id'],
                player_count = count,
                best = votes['best'],
                recc = votes['recommended'],
                nrec = votes['notrecommended'],
                total = votes['total'])
            self.db.add(poll)

        self.db.commit()

    def collection(self, username):
        c = self.db.query(GameCollection).filter(
            GameCollection.bgg_user == username).all()

        if c:
            collection = {'username': username, 'games': []}
            for item in c:
                game = {
                    'bgg_id': item.bgg_id,
                    'stat_ownd': item.stat_ownd,
                    'stat_pown': item.stat_pown,
                    'stat_fort': item.stat_fort,
                    'stat_want': item.stat_want,
                    'stat_wtp': item.stat_wtp,
                    'stat_wtb': item.stat_wtb,
                    'stat_wish': item.stat_wish,
                    'stat_pre': item.stat_pre,
                    'num_plays': item.num_plays,
                    'user_rating': item.user_rating,
                }
                collection['games'].append(game)

            return collection

        return False

    def collection_add(self, collection):
        self.db.query(GameCollection).filter(
            GameCollection.bgg_user == collection['username']).delete()
        for game in collection['games']:
            item = GameCollection(
                bgg_user=collection['username'],
                created_at=datetime.utcnow(),
                **game)
            self.db.add(item)
        self.db.commit()
