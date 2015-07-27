# BGG Stats

A bit of Python code for analyzing the best games for various player counts based on a user's collection on the website Board Game Geek.

## Installation

Requires `Python 2.7.9` and `pip`

1. Install package dependencies `pip install -r requirements.txt`
2. Run `bgg.py`

## Usage

    bgg.py --game=<game>
    bgg.py --u=<username> [--n=<num_players>] [--neg-thresh=<neg>] [--pos-thresh=<POS>] [--include-xpac] [--refresh] [--sort=<sort>]
    bgg.py --top=<top> [--n=<num_players] [--neg-thresh=<neg>] [--pos-thresh=<pos>] [--min-weight=<min>] [--max-weight=<max>] [--min-year=<min>] [--max-year=<max>]

### Options:

    --u=<username>      The Board Game Geek username with the desired collection to analyse.
    --n=<num_players>   Show recommendations for a specific number of players
    --game=<game>       The name of a game to look up.
    --top=<top>         Shows stats on the top X games from Board Game Geek.
    --neg-thresh=<neg>  The number of "Not Recommended" votes to tolerate [default: 0.2].
    --pos-thresh=<neg>  The number of "Best" votes to require [default: 0].
    --include-xpac      Includes game expansions in the results shown.
    --refresh           Fetches the latest Collection data from Board Game Geek.
    --sort=<sort>       How to sort the results, options: perc, rating, weight [default: perc]
    --min-weight=<min>  The minimum weight of game to display.
    --max-weight=<max>  The maxmimum weight of game to display.
    --min-year=<min>    The minimum year of game to display.
    --max-year=<max>    The maxmimum year of game to display.
