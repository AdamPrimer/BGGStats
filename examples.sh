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

./bgg.py --top=1000 --group=players-weight --reddit > examples/bgg_top_1000_player_weight.md

./recc.py --game="Suburbia" > examples/recc_suburbia_top25.md
./recc.py --game="Carcassonne" > examples/recc_carcassonne_top25.md
./recc.py --game="Stone Age" > examples/recc_stone_age_top25.md
./recc.py --game="Tigris & Euphrates" > examples/recc_tigris_and_euphrates_top25.md
./recc.py --game="Keyflower" > examples/recc_keyflower_top25.md
./recc.py --game="Twilight Struggle" > examples/recc_twilight_struggle_top25.md
./recc.py --game="Agricola" > examples/recc_agricola_top25.md
./recc.py --game="The Resistance" > examples/recc_the_resistance_top25.md
./recc.py --game="Puerto Rico" > examples/recc_puerto_rico_top25.md
./recc.py --game="Dominion" > examples/recc_dominion_top25.md
./recc.py --game="Pandemic" > examples/recc_pandemic_top25.md
./recc.py --game="Ticket to Ride" > examples/recc_ticket_to_ride_top25.md
./recc.py --game="Kingsburg" > examples/recc_kingsburg_top25.md
./recc.py --game="Five Tribes" > examples/recc_five_tribes_top25.md

