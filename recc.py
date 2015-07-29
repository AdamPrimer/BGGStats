#!/usr/bin/env python

#!/usr/bin/env python
"""Board Game Geek Recommender

Usage:
  recc.py --game=<game> [--rank-min=<min>]

Options:
  --game=<game>       The name of a game to look up.
  --rank-min=<min>    The [default: 3].
"""

from docopt import docopt

import sys
import cProfile
from itertools import combinations
from datetime import datetime
from collections import defaultdict
from BoardGameGeek import BoardGameGeek

args = docopt(__doc__, version='Board Game Geek Recommender v1.0')

num_games = 500

bgg = BoardGameGeek()

def print_game(res):
    print u"{} ({}) (#{}) (w: {:>3.1f})".format(
        res['name'],
        res['yearpublished'],
        res['rank'],
        res['weight']),
    print u"| {:2.2f} ({:2.2f}) ({})".format(
        res['weighted_rating'], res['rating'], res['ratings'])
    print u"Artists: {}".format(", ".join([x['name'] for x in res['artists']]))
    print u"Categories: {}".format(", ".join([x['name'] for x in res['categories']]))
    print u"Designers: {}".format(", ".join([x['name'] for x in res['designers']]))
    print u"Mechanisms: {}".format(", ".join([x['name'] for x in res['mechanisms']]))
    print u"Publishers: {}".format(", ".join([x['name'] for x in res['publishers']]))
    for i, ans in sorted(res['players_poll'].items()):
        print u"{}: {:>3.0%} {:>3.0%} {:3.0%}".format(
            i,
            ans['best'] / float(ans['total']),
            ans['recommended'] / float(ans['total']),
            ans['notrecommended'] / float(ans['total']))

def load_ratings():
    users = defaultdict(list)
    gcount = defaultdict(float)
    ratings = bgg.all_ratings()
    for bgg_id, bgg_user, rating in ratings.yield_per(100):
        users[bgg_user].append((bgg_id, rating))
        gcount[bgg_id] += 1
    return (users, gcount)

def parse_votes(users, gcount):
    votes = defaultdict(dict)
    for user, ratings in users.iteritems():
        c_rating = 11
        c_rank = 0
        for (game, rating) in sorted(ratings, key=lambda x: x[1], reverse=True):
            if gcount[game] < 100:
                continue

            if rating < c_rating:
                c_rating = rating
                c_rank += 1
            votes[user][game] = c_rank
    return votes

def tally_votes(votes):
    highers = defaultdict(lambda: defaultdict(int))
    for user, ranks in votes.iteritems():
        if game_id not in ranks:
            continue

        rank = ranks[game_id]
        if rank > int(args['--rank-min']):
            continue

        ranks = sorted(ranks.items(), key=lambda x: x[1])
        for rival, rival_rank in ranks:
            if game_id == rival:
                continue

            if rank >= rival_rank:
                highers[game_id][rival] += 1

    return highers

res = bgg.search(query=args['--game'])

if isinstance(res, list):
    for game in sorted(res,
            key=lambda x: (x['rank'] == None, x['rank'])):
        print_game(game)
        print ""
    sys.exit()

print u"# Recommendations for {} ({})".format(res['name'], res['yearpublished'])
print u""

print "__BGG Rank__: {}".format(res['rank'])
print "__Weight__: {}".format(res['weight'])
print "__Length__: {}".format(res['maxplaytime'])
print ""

game_id = res['bgg_id']

sys.stderr.write("Loading Ratings\n")
(users, gcount) = load_ratings()
sys.stderr.write("Parsing User Votes\n")
votes = parse_votes(users, gcount)
sys.stderr.write("Tallying User Votes\n\n")
highers = tally_votes(votes)

weighted = []
for game, score in sorted(highers[game_id].items(), key=lambda x: x[1], reverse=True):
    g = bgg.get_game(game)
    weighted.append((g, score, score / float(g['ratings'])))

print u"BGG Rank | Votes | Score | Weight | Length | Year | Game"
print u"---------|-------|-------|--------|--------|------|-----"
for game, votes, score in sorted(weighted, key=lambda x: x[2], reverse=True)[:25]:
    stars = ""
    print u"{} | {} | {:>2.4f} | {:>3.1f} | {} min | {} | {}[{}]({})".format(
        game['rank'],
        votes,
        score,
        game['weight'],
        game['maxplaytime'],
        game['yearpublished'],
        stars, game['name'],
        "https://boardgamegeek.com/boardgame/{}".format(
            game['bgg_id'])
    )

print ""
print "## Explanation of Score: ##\n"
print "1. Look at the votes for the Top {} games on BGG".format(num_games)
print "2. Rank each user's votes for these games (1 is highest)."
print u"3. For each user that has the game \"{}\" no lower than rank {} ".format(
    args['--game'], args['--rank-min'])
u"see what other games that user has ranked at least as high."
print "4. Count how many users have each other game that meet this criterion"
print "5. Divide the number of votes by the total number of ratings for the game"
