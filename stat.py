#!/usr/bin/env python
"""Board Game Geek Stats

Usage:
  stats.py --u=<username> [--n=<num_players>] [--neg-thresh=<neg>]
  [--pos-thresh=<POS>] [--include-xpac] [--refresh] [--sort=<sort>]

Options:
  --u=<username>      The Board Game Geek username with the desired collection to analyse.
  --n=<num_players>   Show recommendations for a specific number of players
  --neg-thresh=<neg>  The number of "Not Recommended" votes to tolerate [default: 0.2].
  --pos-thresh=<neg>  The number of "Best" votes to require [default: 0.2].
  --include-xpac      Includes game expansions in the results shown.
  --refresh           Fetches the latest Collection data from Board Game Geek.
  --sort=<sort>       How to sort the results, options: perc, rating, weight [default: perc]
"""

from datetime import datetime
from collections import defaultdict
from BoardGameGeek import BoardGameGeek

from docopt import docopt

def set_best_perc(collection, num_players):
    best = set()
    for game in collection:
        ans = game['players_poll'][num_players]
        perc = ans['best'] / float(ans['total']) * 100
        best.add((perc, game['user_rating'], game['weight'], game))
    return best

def print_games(collection, sort_by="perc"):
    sorted_res = sorted(collection, reverse=True)
    if sort_by == "rating":
        sorted_res = sorted(collection, reverse=True, key=lambda x: x[1])
    elif sort_by == "weight":
        sorted_res = sorted(collection, reverse=True, key=lambda x: x[2])

    for perc, rating, weight, game in sorted_res:
        if rating and rating != 'N/A':
            print "  ({:>3.0f}%) ({:>4.1f}) (w: {:>3.1f}) {}".format(
                perc, rating, weight, game['name'])
        else:
            print "  ({:>3.0f}%) ( N/A) (w: {:>3.1f}) {}".format(perc, game['weight'], game['name'])
    print ""

if __name__ == '__main__':
    args = docopt(__doc__, version='Board Game Geek Stats v1.0')

    bgg = BoardGameGeek()

    '''
    limit = 1000
    min_weight = 2.8
    num_players = 5
    neg_thresh = float(args['--neg-thresh'])
    pos_thresh = float(args['--pos-thresh'])

    top_100 = bgg.top_100(limit=limit)[:limit]
    print u"Board Game Geek Top {}".format(limit)
    for i, game in enumerate(sorted(top_100, reverse=True,
            key=lambda x: x['best'] / float(x['total']))):
        if game['weight'] < min_weight:
            continue
        if game['maxplayers'] < num_players:
            continue
        if num_players not in game['players_poll']:
            continue
        six = game['players_poll'][num_players]
        if six['notrecommended'] / float(six['total']) > neg_thresh:
            continue
        perc = six['best'] / float(six['total'])
        if perc < pos_thresh:
            continue

        print u"  ({:>3}) ({:>3.0%}) (w: {:>3.1f}) {}".format(
            i+1, perc, game['weight'], game['name'])
    print ""

    exit()
    '''

    username = args['--u']
    col = bgg.get_collection(username, refresh=args['--refresh'], include_xpac=args['--include-xpac'])

    if args['--n']:
        num_players = int(args['--n'])

        print "Games Played Best with {} Players".format(num_players)
        best = set_best_perc(col.best_at(num_players), num_players)
        print_games(best, sort_by=args['--sort'])

        print "Games Played Well with {} Players".format(num_players)
        good = set_best_perc(col.good_at(
                num_players,
                neg_thresh=float(args['--neg-thresh']),
                pos_thresh=float(args['--pos-thresh'])), num_players)
        print_games(good.difference(best), sort_by=args['--sort'])

    else:
        for num_players, games in col.best_at():
            if not num_players:
                continue

            print "Games Played Best with {} Players".format(num_players)
            best = set_best_perc(games, num_players)
            print_games(best, sort_by=args['--sort'])

