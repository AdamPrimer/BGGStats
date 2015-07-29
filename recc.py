#!/usr/bin/env python
#coding: utf8
"""Board Game Geek Recommender

Usage:
  recc.py --game=<game> [--rank-min=<min>] [--thresh=<thresh>] [--limit=<limit>]

Options:
  --game=<game>       The name of a game to look up.
  --rank-min=<min>    The [default: 3].
  --thresh=<thresh>   The [default: 50].
  --limit=<limit>     The [default: 25].
"""

import sys
import math
import codecs
import locale

sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

from docopt import docopt

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
    likers = defaultdict(int)
    for user, ranks in votes.iteritems():
        ranks = sorted(ranks.items(), key=lambda x: x[1])
        for game, rank in ranks:
            if rank > int(args['--rank-min']):
                break

            likers[game] += 1

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

    return (highers, likers)

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

sys.stderr.write(u"Getting Ratings for {}\n".format(res['name']))
ratings = bgg.ratings(game_id)

sys.stderr.write("Loading Ratings\n")
(users, gcount) = load_ratings()
sys.stderr.write("Parsing User Votes\n")
votes = parse_votes(users, gcount)
sys.stderr.write("Tallying User Votes\n\n")
highers, likers = tally_votes(votes)

weighted = []
for game, score in sorted(highers[game_id].items(), key=lambda x: x[1], reverse=True):
    g = bgg.get_game(game)
    if score >= int(args['--thresh']):
        weighted.append((g, score, score / float(likers[game])))

print u"BGG Rank | Votes |  Score | Weight | Length | Year | Game"
print u"---------|-------|--------|--------|--------|------|-----"
limit = int(args['--limit'])
weighted = sorted(weighted, key=lambda x: x[2], reverse=True)[:int(1.5 * limit)]
weighted = sorted(weighted, key=lambda x: math.log(x[1]) * x[2], reverse=True)[:limit]
for game, votes, score in weighted:
    stars = ""
    print u"{:>8} | {:>5} | {:>0.2%} | {:>6.1f} | {:>3} min | {} | {}[{}]({})".format(
        game['rank'],
        votes,
        score,
        game['weight'],
        game['maxplaytime'],
        game['yearpublished'],
        stars, game['name'],
        u"https://boardgamegeek.com/boardgame/{}".format(
            game['bgg_id'])
    )

print ""
print "## Explanation of Score: ##\n"
print "1. Look at the votes for the Top {} games on BGG".format(num_games)
print "2. Rank each user's votes for these games (1 is highest)."
print u"3. For each user that has the game \"{}\" no lower than rank {}".format(
    args['--game'], args['--rank-min']),
print u"see what other games that user has ranked at least as high."
print "4. Count how many users have each other game that meet this criterion"
print "5. Divide the number of votes by the total number of people that like the game"
print ""

print "## Interpretation of Score: ##\n"
print u"The percentage of people that like the recommended game, that also like {}.".format(
    args['--game'])
print ""

print "## Sorting: ##\n"
print "The top {} games when sorted by `score` are re-sorted".format(
    int(limit * 1.5)),
print "by `log(votes) * score`, then the top {} of those are presented.".format(
    limit)
print "\nThis works to rank games with more votes higher, without having really popular games dominate the rankings."
