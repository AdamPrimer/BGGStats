#!/usr/bin/env python
"""Board Game Geek Info

Usage:
  bgg.py --u=<username> [--n=<num_players>] [--neg-thresh=<neg>]
  [--pos-thresh=<POS>] [--include-xpac] [--refresh] [--sort=<sort>]
  bgg.py --game=<game>
  bgg.py --top=<top> [--n=<num_players] [--neg-thresh=<neg>]
  [--pos-thresh=<pos>] [--min-weight=<min>] [--max-weight=<max>]
  [--min-year=<min>] [--max-year=<max>] [--max-length=<max>] [--group=<group]
  [--reddit] [--category=<category>...] [--nmax=<n>]

Options:
  --u=<username>      The Board Game Geek username with the desired collection to analyse.
  --n=<num_players>   Show recommendations for a specific number of players
  --nmax=<num_players>  Show recommendations for a specific number of players
  --game=<game>       The name of a game to look up.
  --top=<top>         Shows stats on the top X games from Board Game Geek.
  --neg-thresh=<neg>  The number of "Not Recommended" votes to tolerate [default: 0.25].
  --pos-thresh=<neg>  The number of "Best" votes to require [default: 0].
  --include-xpac      Includes game expansions in the results shown.
  --refresh           Fetches the latest Collection data from Board Game Geek.
  --sort=<sort>       How to sort the results, options: perc, rating, weight [default: perc]
  --min-weight=<min>  The minimum weight of game to display.
  --max-weight=<max>  The maxmimum weight of game to display.
  --min-year=<min>    The minimum year of game to display.
  --max-year=<max>    The maxmimum year of game to display.
  --max-length=<max>    The maxmimum length of game to display.
  --group=<group>     Options: year, players, mechanism, mechanism-pair, weight, weight-individual
  --reddit
"""

import cProfile
from itertools import combinations
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

def print_filt_game(i, game, num_players, markdown=False):
    if not markdown:
        if num_players:
            six = game['players_poll'][num_players]
            perc = six['best'] / float(six['total'])
            print u"\t({:>3}) ({:>3.0%}) ({:3.0%}) (w: {:>3.1f}, {} min) {}".format(
                game['rank'], perc,
                (six['best'] + six['recommended']) / float(six['total']),
                game['weight'], game['maxplaytime'], game['name'])
        else:
            print u"\t({:>3}) (w: {:>3.1f}, {} min) {}".format(
                game['rank'], game['weight'], game['maxplaytime'], game['name'])
    else:
        stars = u""
        if [x for x in game['categories'] if x['name'] == "Wargame"]:
            stars = u"*** "

        if num_players:
            six = game['players_poll'][num_players]
            perc = six['best'] / float(six['total'])
            print u"{:>3} | {:>3.0%} | {:3.0%} | {:>3.1f} | {} min | {} | {}[{}]({})".format(
                game['rank'], perc,
                (six['best'] + six['recommended']) / float(six['total']),
                game['weight'], game['maxplaytime'],
                game['yearpublished'], stars, game['name'],
                "https://boardgamegeek.com/boardgame/{}".format(game['bgg_id']))

        else:
            print u"{:>3} | {:>3.1f} | {} min | {} | {}[{}]({})".format(
                game['rank'], game['weight'], game['maxplaytime'],
                game['yearpublished'], stars, game['name'],
                "https://boardgamegeek.com/boardgame/{}".format(game['bgg_id']))

if __name__ == '__main__':
    args = docopt(__doc__, version='Board Game Geek Stats v1.0')

    bgg = BoardGameGeek()

    if args['--top']:
        limit = int(args['--top'])

        min_weight = 0
        if args['--min-weight']:
            min_weight = float(args['--min-weight'])

        max_weight = 5
        if args['--max-weight']:
            max_weight = float(args['--max-weight'])

        num_players = None
        if args['--n']:
            num_players = int(args['--n'])

        nmax = num_players
        if args['--nmax']:
            nmax = int(args['--nmax'])

        max_length = 9999
        if args['--max-length']:
            max_length = int(args['--max-length'])

        max_year = 9999
        if args['--max-year']:
            max_year = int(args['--max-year'])

        min_year = -9999
        if args['--min-year']:
            min_year = int(args['--min-year'])

        neg_thresh = float(args['--neg-thresh'])
        pos_thresh = float(args['--pos-thresh'])



        top_100 = bgg.top_100(limit=limit)[:limit]

        filtered = []
        for i, game in enumerate(top_100):
            if args['--category']:
                overlap = [x for x in game['categories'] if x['name'] in
                        args['--category']]
                if not overlap:
                    continue
            if game['weight'] < min_weight:
                continue
            if game['weight'] > max_weight:
                continue
            if game['yearpublished'] > max_year:
                continue
            if game['maxplaytime'] > max_length:
                continue
            if args['--min-year'] and game['yearpublished'] < min_year:
                continue
            if num_players:
                skip = False
                for i in xrange(num_players, nmax + 1):
                    if game['maxplayers'] < i:
                        skip = True
                        break
                    if i not in game['players_poll']:
                        skip = True
                        break
                    six = game['players_poll'][i]
                    if six['notrecommended'] / float(six['total']) > neg_thresh:
                        skip = True
                        break
                    perc = six['best'] / float(six['total'])
                    if perc < pos_thresh:
                        skip = True
                        break
                if skip:
                    continue

            filtered.append(game)

        if not args['--group']:
            print u"Board Game Geek Top {} ({} results)".format(limit, len(filtered))
            if args['--reddit']:
                print "BGG Rank | Best | Recommend | Weight | Length | Year | Game"
                print "---------|------|-----------|--------|--------|------|-----"
            for i, game in enumerate(filtered):
                print_filt_game(i, game, num_players, args['--reddit'])
            print ""

        elif args['--group'] == 'year':
            grouped = defaultdict(list)
            for game in filtered:
                grouped[game['yearpublished']].append(game)

            print "# Top {} by Year".format(len(filtered))
            print ""
            for num, games in sorted(grouped.items()):
                print "## {} ({} results, {:>3.1%})".format(num, len(games),
                        len(games)/float(len(filtered)))
                print ""
                for game in games:
                    print_filt_game(i, game, num_players)
                print ""

        elif args['--group'] == 'weight':
            grouped = defaultdict(list)
            for game in filtered:
                grouped[int(game['weight'])].append(game)

            print "# Top {} by Weight (Grouped)".format(len(filtered))
            print ""
            for num, games in sorted(grouped.items()):
                print "## {} ({} results, {:>3.1%})".format(num, len(games),
                        len(games)/float(len(filtered)))
                print ""
                for game in games:
                    print_filt_game(i, game, num_players)
                print ""

        elif args['--group'] == 'weight-individual':
            grouped = defaultdict(list)
            for game in filtered:
                grouped[round(game['weight'], 1)].append(game)

            print "# Top {} by Weight (Individual)".format(len(filtered))
            print ""
            for num, games in sorted(grouped.items()):
                print "## {:2.1f} ({} results, {:>3.1%})".format(num, len(games),
                        len(games)/float(len(filtered)))
                print ""
                for game in games:
                    print_filt_game(i, game, num_players)
                print ""

        elif args['--group'] == 'players':
            grouped = defaultdict(list)
            for game in filtered:
                for x in xrange(game['minplayers'], game['maxplayers'] + 1):
                    grouped[x].append(game)

            print "# Top {} by Player Count".format(len(filtered))
            print ""
            for num, games in sorted(grouped.items()):
                print "## {} ({} results, {:>3.1%})".format(num, len(games),
                        len(games)/float(len(filtered)))
                print ""
                for game in games:
                    print_filt_game(i, game, num_players)
                print ""

        elif args['--group'] == 'mechanism':
            grouped = defaultdict(list)
            for game in filtered:
                for mech in game['mechanisms']:
                    grouped[mech['name']].append(game)

            print "# Top {} by Mechanism".format(len(filtered))
            print ""
            for num, games in sorted(grouped.items(), key=lambda x: len(x[1]),
                    reverse=True):
                print "## {} ({} results, {:>3.1%})".format(num, len(games),
                        len(games)/float(len(filtered)))
                print ""
                for game in games:
                    print_filt_game(i, game, num_players)
                print ""

        elif args['--group'] == 'mechanism-pair':
            grouped = defaultdict(list)
            for game in filtered:
                for mech, mech2 in combinations(game['mechanisms'], 2):
                    grouped[(mech['name'], mech2['name'])].append(game)

            print "# Top {} by Mechanism Pairing".format(len(filtered))
            print ""
            for num, games in sorted(grouped.items(), key=lambda x: len(x[1]),
                    reverse=True):
                if len(games) == 1:
                    continue
                print "## {} and {} ({} results, {:>3.1%})".format(num[0], num[1], len(games),
                        len(games)/float(len(filtered)))
                print ""
                for game in games:
                    print_filt_game(i, game, num_players)
                print ""

        elif args['--group'] == "rating":
            for game in filtered:
                print "Getting Ratings for {}".format(game['name'])
                ratings = bgg.ratings(game['bgg_id'])


    elif args['--game']:
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
