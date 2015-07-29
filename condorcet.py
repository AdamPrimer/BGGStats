#!/usr/bin/env python
import cProfile
from itertools import combinations
from datetime import datetime
from collections import defaultdict
from BoardGameGeek import BoardGameGeek

num_games = 500

bgg = BoardGameGeek()
top_100 = bgg.top_100(limit=num_games)

#print "Loading Ratings"
def load_ratings():
    users = defaultdict(list)
    ratings = bgg.all_ratings()
    for bgg_id, bgg_user, rating in ratings.yield_per(100):
        users[bgg_user].append((bgg_id, rating))
    return users

users = load_ratings()
#print ""

#print "Parsing User Votes"
def parse_votes(users):
    votes = defaultdict(dict)
    for user, ratings in users.iteritems():
        c_rating = 11
        c_rank = 0
        for (game, rating) in sorted(ratings, key=lambda x: x[1], reverse=True):
            if rating < c_rating:
                c_rating = rating
                c_rank += 1
            votes[user][game] = c_rank
    return votes

votes = parse_votes(users)
#print ""

#print "Tallying User Votes"
def tally_votes(votes):
    highers = defaultdict(lambda: defaultdict(int))
    for user, ranks in votes.iteritems():
        ranks = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
        for i, (game, rank) in enumerate(ranks):
            for rival, rival_rank in ranks[:i+1]:
                if rank < rival_rank:
                    highers[game][rival] += 1
    return highers

highers = tally_votes(votes)
#print ""

#print "Determining Paired Wins {}".format(len(top_100))
results = dict()
for game in top_100:
    wins = []
    losses = []
    ties = []
    g_id = game['bgg_id']

    for rival in top_100:
        r_id = rival['bgg_id']

        if g_id == r_id:
            continue

        # Note: highers[r_id][g_id] == lowers[g_id][r_id]

        if highers[g_id][r_id] > highers[r_id][g_id]:
            wins.append(r_id)
        if highers[g_id][r_id] < highers[r_id][g_id]:
            losses.append(r_id)
        if highers[g_id][r_id] and highers[g_id][r_id] == highers[r_id][g_id]:
            ties.append(r_id)

    results[g_id] = (wins, losses, ties)
#print ""

def condorcet(results):
    condorcet = []

    for game, res in results.iteritems():
        condorcet.append((
            game, len(res[0]) * 2 + len(res[2])
        ))

    return sorted(condorcet, key=lambda x: x[1], reverse=True)

def condorcet_irv(results):
    condorcet = []

    while len(results.items()) > 0:
        found = False
        for game, res in results.iteritems():
            # Find a unanimous winner
            if len(res[0]) == len(results) - 1:
                print "Winner: {}".format(game)
                condorcet.append(game)
                found = game
                break

        if found:
            for game, res in results.iteritems():
                try:
                    res[0].remove(found)
                except ValueError:
                    pass
                try:
                    res[1].remove(found)
                except ValueError:
                    pass
                try:
                    res[2].remove(found)
                except ValueError:
                    pass

            del results[found]
        else:
            break

    return condorcet

ups = []
downs = []
nomove = []

print u"# BGG Top {} (Condorcet)".format(num_games)
print ""
#print ""
for i, (game, score) in enumerate(condorcet(results)):
    rank = i + 1
    g = bgg.get_game(game)
    old_rank = g['rank']
    diff = rank - old_rank
    if diff > 0:
        downs.append((g, rank, diff))
    elif diff < 0:
        ups.append((g, rank, diff))
    else:
        nomove.append((g, rank, diff))

    print u"{:>3} | {:>3} | {:>4} | {}".format(rank, g['rank'], diff, g['name'])
print ""

print "## Moved Down"
print ""

for g, rank, diff in sorted(downs, key=lambda x: x[2], reverse=True):
    print u"{:>3} | {:>3} | {:>4} | {:>2.1f} | {}".format(rank, g['rank'], diff,
    g['weight'], g['name'])
print ""

print "## Moved Up"
print ""
for g, rank, diff in sorted(ups, key=lambda x: x[2]):
    print u"{:>3} | {:>3} | {:>4} | {:>2.1f} | {}".format(rank, g['rank'], diff, g['weight'], g['name'])
print ""

print "## Didn't Move"
print ""
for g, rank, diff in sorted(nomove, key=lambda x: x[1]):
    print u"{:>3} | {:>3} | {:>4} | {:>2.1f} | {}".format(rank, g['rank'], diff,
            g['weight'], g['name'])
print ""

print "Average Up Weight: {}".format(
    sum([g['weight'] for g, _, _ in ups]) / float(len(ups)))
print "Average Down Weight: {}".format(
    sum([g['weight'] for g, _, _ in downs]) / float(len(downs)))
