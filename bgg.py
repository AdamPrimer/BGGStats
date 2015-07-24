#!/usr/bin/env python
"""Board Game Geek Stats

Usage:
  bgg.py --u=<username> [--n=<num_players>] [--neg-thresh=<neg>]
  [--pos-thresh=<POS>] [--include-xpac] [--refresh] [--sort=<sort>]
  bgg.py --game=<game>

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
            print u"  ({:>3.0f}%) ({:>4.1f}) (w: {:>3.1f}) {}".format(
                perc, rating, weight, game['name'])
        else:
            print u"  ({:>3.0f}%) ( N/A) (w: {:>3.1f}) {}".format(perc, game['weight'], game['name'])
    print ""

def print_game(res):
    print u"{} ({}) (#{}) (w: {:>3.1f})".format(
        res['name'],
        res['yearpublished'],
        res['rank'],
        res['weight']),
    print "| {:2.2f} ({:2.2f}) ({})".format(
        res['weighted_rating'], res['rating'], res['ratings'])
    print "Artists: {}".format(", ".join([x['name'] for x in res['artists']]))
    print "Categories: {}".format(", ".join([x['name'] for x in res['categories']]))
    print "Designers: {}".format(", ".join([x['name'] for x in res['designers']]))
    print "Mechanisms: {}".format(", ".join([x['name'] for x in res['mechanisms']]))
    print "Publishers: {}".format(", ".join([x['name'] for x in res['publishers']]))
    for i, ans in sorted(res['players_poll'].items()):
        print "{}: {:>3.0%} {:>3.0%} {:3.0%}".format(
            i,
            ans['best'] / float(ans['total']),
            ans['recommended'] / float(ans['total']),
            ans['notrecommended'] / float(ans['total']))

if __name__ == '__main__':
    args = docopt(__doc__, version='Board Game Geek Stats v1.0')

    bgg = BoardGameGeek()

    if args['--game']:
        res = bgg.search(query=args['--game'])
        if isinstance(res, list):
            for game in sorted(res,
                    key=lambda x: (x['rank'] == None, x['rank'])):
                print_game(game)
                print ""
        else:
            print_game(res)

    else:
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
