#!/usr/bin/env bash
./bgg.py --top=100 --group=year > examples/bgg_top_100_by_year.md
./bgg.py --top=100 --group=players > examples/bgg_top_100_by_players.md
./bgg.py --top=100 --group=mechanism > examples/bgg_top_100_by_mechanism.md
./bgg.py --top=100 --group=mechanism-pair > examples/bgg_top_100_by_mechanism_pair.md
./bgg.py --top=100 --group=weight > examples/bgg_top_100_by_weight.md
./bgg.py --top=100 --group=weight-individual > examples/bgg_top_100_by_weight_individual.md

./bgg.py --top=200 --group=year > examples/bgg_top_200_by_year.md
./bgg.py --top=200 --group=players > examples/bgg_top_200_by_players.md
./bgg.py --top=200 --group=mechanism > examples/bgg_top_200_by_mechanism.md
./bgg.py --top=200 --group=mechanism-pair > examples/bgg_top_200_by_mechanism_pair.md
./bgg.py --top=200 --group=weight > examples/bgg_top_200_by_weight.md
./bgg.py --top=200 --group=weight-individual > examples/bgg_top_200_by_weight_individual.md

./bgg.py --top=500 --group=year > examples/bgg_top_500_by_year.md
./bgg.py --top=500 --group=players > examples/bgg_top_500_by_players.md
./bgg.py --top=500 --group=mechanism > examples/bgg_top_500_by_mechanism.md
./bgg.py --top=500 --group=mechanism-pair > examples/bgg_top_500_by_mechanism_pair.md
./bgg.py --top=500 --group=weight > examples/bgg_top_500_by_weight.md
./bgg.py --top=500 --group=weight-individual > examples/bgg_top_500_by_weight_individual.md

./recc.py --game="Suburbia" > examples/recc_suburbia_top25.md
