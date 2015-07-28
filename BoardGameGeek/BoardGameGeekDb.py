from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, exc
from BoardGameGeekDbSchema import (
    Base,
    Game,
    GamePlayerPoll,
    GameCollection,
    Artist,
    Category,
    Designer,
    Mechanism,
    Publisher,
    GameArtist,
    GameCategory,
    GameDesigner,
    GameMechanism,
    GamePublisher,
    GameRating,
)

class BoardGameGeekDb:
    def __init__(self, path):
        engine = create_engine(path)
        #engine.echo = True
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.db = DBSession()

    def has_game(self, bgg_id):
        try:
            c = self.db.query(Game).filter(
                Game.bgg_id == bgg_id).one()
            return True
        except exc.NoResultFound:
            return False

    def games(self, limit=100):
        res = self.db.query(Game).filter(
            Game.rank <= limit).all()
        if res:
            games = [self.get_game(r.bgg_id, r) for r in res]
            return self.games_extended_info(games)
        return False

    def games_extended_info(self, games):
        games = {r['bgg_id']: r for r in games}

        artists = {}
        categories = {}
        designers = {}
        mechanisms = {}
        publishers = {}

        r_artists = self.db.query(Artist).all()
        r_categories = self.db.query(Category).all()
        r_designers = self.db.query(Designer).all()
        r_mechanisms = self.db.query(Mechanism).all()
        r_publishers = self.db.query(Publisher).all()

        g_artists = self.db.query(GameArtist).all()
        g_categories = self.db.query(GameCategory).all()
        g_designers = self.db.query(GameDesigner).all()
        g_mechanisms = self.db.query(GameMechanism).all()
        g_publishers = self.db.query(GamePublisher).all()

        g_polls = self.db.query(GamePlayerPoll).all()

        for artist in r_artists:
            artists[artist.art_id] = artist.name

        for category in r_categories:
            categories[category.cat_id] = category.name

        for designer in r_designers:
            designers[designer.des_id] = designer.name

        for mechanism in r_mechanisms:
            mechanisms[mechanism.mec_id] = mechanism.name

        for publisher in r_publishers:
            publishers[publisher.pub_id] = publisher.name

        for item in g_polls:
            game = games.get(item.bgg_id, False)
            if game:
                game['players_poll'][item.player_count] = {
                    'best': item.best,
                    'recommended': item.recc,
                    'notrecommended': item.nrec,
                    'total': item.total,
                }

        for artist in g_artists:
            game = games.get(artist.bgg_id, False)
            if game:
                game['artists'].append({
                    'art_id': artist.art_id,
                    'name': artists[artist.art_id]})

        for category in g_categories:
            game = games.get(category.bgg_id, False)
            if game:
                game['categories'].append({
                'cat_id': category.cat_id,
                'name': categories[category.cat_id]})

        for designer in g_designers:
            game = games.get(designer.bgg_id, False)
            if game:
                game['designers'].append({
                'des_id': designer.des_id,
                'name': designers[designer.des_id]})

        for mechanism in g_mechanisms:
            game = games.get(mechanism.bgg_id, False)
            if game:
                game['mechanisms'].append({
                'mec_id': mechanism.mec_id,
                'name': mechanisms[mechanism.mec_id]})

        for publisher in g_publishers:
            game = games.get(publisher.bgg_id, False)
            if game:
                game['publishers'].append({
                'pub_id': publisher.pub_id,
                'name': publishers[publisher.pub_id]})

        return sorted(games.values(), key=lambda x: x['rank'])

    def game(self, bgg_id):
        try:
            raw = self.db.query(Game).filter(
                Game.bgg_id == bgg_id).one()
        except exc.NoResultFound:
            return False

        return self.get_game(bgg_id, raw)

    def get_game(self, bgg_id, c):
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
            'weighted_rating': c.weighted_rating,
            'user_rating': 'N/A',
            'rating': c.rating,
            'ratings': c.ratings,
            'rank': c.rank,
            'players_poll': {},
            'artists': [],
            'categories': [],
            'designers': [],
            'mechanisms': [],
            'publishers': [],
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
            rank = game.get('rank', None),
            ratings = game['ratings'],
            weighted_rating = game['weighted_rating'],
            rating = game['rating'],
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

        for art in game['artists']:
            self.artist_add(art, game['bgg_id'])
        for art in game['designers']:
            self.designer_add(art, game['bgg_id'])
        for art in game['categories']:
            self.category_add(art, game['bgg_id'])
        for art in game['mechanisms']:
            self.mechanism_add(art, game['bgg_id'])
        for art in game['publishers']:
            self.publisher_add(art, game['bgg_id'])

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

    def has_rankings(self, limit=100):
        res = self.db.query(Game).filter(
            Game.rank == limit).count()
        if res:
            return True
        else:
            return False


    def ratings(self, bgg_id):
        res = self.db.query(GameRating.bgg_id, GameRating.bgg_user, GameRating.rating)
        if res:
            return res
        else:
            return False

    def has_ratings(self, bgg_id):
        res = self.db.query(GameRating).filter(
            GameRating.bgg_id == bgg_id).count()
        if res:
            return True
        else:
            return False

    def ratings_add(self, bgg_id, ratings):
        self.db.query(GameRating).filter(
            GameRating.bgg_id == bgg_id).delete()
        for rating in ratings:
            item = GameRating(
                bgg_user=rating['username'],
                bgg_id=rating['bgg_id'],
                rating=rating['rating'],
                created_at=datetime.utcnow())
            self.db.add(item)
        self.db.commit()

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

    def game_generic(self, generic, bgg_id, cls, idx):
        try:
            gen = self.db.query(cls).filter(
                getattr(cls, idx) == generic[idx]).filter(
                cls.bgg_id == bgg_id).one()
            return gen
        except exc.NoResultFound:
            return False

    def cls_generic(self, generic, cls, idx):
        try:
            gen = self.db.query(cls).filter(
                getattr(cls, idx) == generic[idx]).one()
            return gen
        except exc.NoResultFound:
            return False

    def cls_generic_add(self, generic, bgg_id, cls1, cls2, idx):
        gen = self.cls_generic(generic, cls1, idx)
        if not gen:
            self.db.add(cls1(
                name=generic['name'],
                **{idx: generic[idx]}))
            self.db.commit()
            gen = self.cls_generic(generic, cls1, idx)

        if not self.game_generic(generic, bgg_id, cls2, idx):
            self.db.add(cls2(
                bgg_id=bgg_id,
                **{idx: generic[idx]}))
            self.db.commit()

        return gen

    def artist(self, artist):
        return self.cls_generic(artist, Artist, 'art_id')

    def artist_add(self, artist, bgg_id):
        return self.cls_generic_add(
            artist, bgg_id, Artist, GameArtist, 'art_id')

    def category(self, category):
        return self.cls_generic(category, Category, 'cat_id')

    def category_add(self, category, bgg_id):
        return self.cls_generic_add(
            category, bgg_id, Category, GameCategory, 'cat_id')

    def designer(self, designer):
        return self.cls_generic(designer, Designer, 'des_id')

    def designer_add(self, designer, bgg_id):
        return self.cls_generic_add(
            designer, bgg_id, Designer, GameDesigner, 'des_id')

    def mechanism(self, mechanism):
        return self.cls_generic(mechanism, Mechanism, 'mec_id')

    def mechanism_add(self, mechanism, bgg_id):
        return self.cls_generic_add(
            mechanism, bgg_id, Mechanism, GameMechanism, 'mec_id')

    def publisher(self, publisher):
        return self.cls_generic(publisher, Publisher, 'pub_id')

    def publisher_add(self, publisher, bgg_id):
        return self.cls_generic_add(
            publisher, bgg_id, Publisher, GamePublisher, 'pub_id')
