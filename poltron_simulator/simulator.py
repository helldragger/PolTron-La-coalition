# -*- coding: utf-8 -*-
from math import ceil, floor, sqrt
from random import shuffle
from typing import Tuple

import poltron_util.progress_bar as pb
from poltron_game.Game import Game
from poltron_model import model
from poltron_util import map_size


est_duration_secs = 10
est_cases_per_sec_per_player = 1
est_cases_per_player = est_duration_secs * est_cases_per_sec_per_player


def parameterize_c(m: int, n: int, min_c: int, max_c: int) -> Tuple[int, int]:
    # coalition size is generated depending on the size as explained:
    # Taking a total of approx 5 move per second for a human player (as in Tron
    # armageddon)
    # we determine 5 moves (ticks) necessary per second per IA.
    # Taking a game estimated span of 1 minute (60 sec), we can say our map area
    # (MxN) must be at least equal to (60*5) cases per player, so 60*5*(C+1)
    # Therefore, we approximate using a wild guess ignoring the fact players
    # might die and leave more cases per player that C = ((MxN)/(300))-1
    # we will floor it to avoid accidentally overcrowd our population
    area = m * n
    max_c = min(floor(area / est_cases_per_player) - 1, max(max_c, 1))

    return min_c, max_c


def parameterize_m(ds: int, size: int) -> int:
    """
    Pour calculer la taille du plateau nous partons du principe que que ceux
    ci seront toujours carrés et que nous n'aurons que trois tailles de plateau:
       -petit
       -moyen
       -grand

    Ces tailles représentent des cartes où la profondeur de recherche maximale
    doit avoir une surface de respectivement 75%, 50% et 25% de la carte.

    La superficie prise en compte par un joueur d'intelligence n sur notre
    plateau est calculable ainsi: 4*(1+2+3+....n) or ceci est une somme connue donc
       -> 4*(1+2+3...+n) = 4*( n*(n+1)/2 )
       superficie player -> 2n(n+1)

    La superficie voulue du plateau est donc calculée ainsi pour chaque taille:
    -   petit   ->  2n(n+1)/0.75
    -   moyen   ->  2n(n+1)/0.50
    -   grand   ->  2n(n+1)/0.25

    La largeur du plateau devant être un nombre entier, nous allons donc
    arondir au supérieur la racine de notre superficie.
    Largeur = Longueur = ceil(sqrt(superficie map))

    """
    if size == map_size.SMALL:
        return ceil(sqrt(2 * ds * (ds + 1) / 0.75))
    elif size == map_size.MEDIUM:
        return ceil(sqrt(2 * ds * (ds + 1) / 0.5))
    elif size == map_size.LARGE:
        return ceil(sqrt(2 * ds * (ds + 1) / 0.25))


def simulate_game(args, model_mode):
    import poltron_db.db as db
    size, size_name, c, ds, dc = args
    m = parameterize_m(ds, size)
    game_id = db.get_last_game_id() + 1
    if model_mode:
        game = model.Model(m, m, c, ds, dc)
        game.run()
    else:
        game = Game(m, m, c, ds, dc)
        game.run()

    db.insert_game_info(game_id, size_name, m, m, ds, dc, c)

    db.insert_game_result(game_id, game.tick, game.victory)

    # for tick, deaths in game.deaths:
    #    db.insert_deaths(game_id, tick, deaths)
    #
    # for tick, nb_walls, c_deaths in game.important_moments:
    #    db.insert_important_moment(game_id, tick, nb_walls, c_deaths)
    #
    # for player_id, x, y in game.initial_positions:
    #    db.insert_initial_positions(game_id, player_id, x, y)
    #
    # for player_id, player_order in game.initial_order:
    #    db.insert_player_order(game_id, player_id, player_order)
    return


def print_search_space(ds_values: set, dc_values: set, c_values) -> None:
    min_m = parameterize_m(min(ds_values), map_size.SMALL)
    max_m = parameterize_m(max(ds_values), map_size.LARGE)

    print(f"Tested Ds values: {ds_values}")
    print(f"Tested Dc values: {dc_values}")
    print(f"Tested coalition sizes: {c_values}")
    print(f"Smallest map dimensions: {min_m}x{min_m}")
    print(f"Largest map dimensions: {max_m}x{max_m}")
    print("\n")


def estimate_time_before_arrival(secs: int):
    mins = max(0, secs // 60)
    hours = max(0, mins // 60)
    days = max(0, hours // 24)

    hours %= 24
    mins %= 60
    secs %= 60

    return f"{int(days)}d {int(hours)}h {int(mins)}m {int(secs)}s"


def generate_data(iteration_per_combination: int, model_mode: bool) -> None:
    import time
    map_sizes: set = {(map_size.SMALL, "1.S"), (map_size.MEDIUM, "2.M"),
                      (map_size.LARGE, "3.L")}
    ds_values: set = {4, 5, 6, 7}
    dc_values: set = {x for x in range(3, max(ds_values), 1)}

    c_values: set = {2, 3, 4, 5}
    # 3 sizes of map
    # 3 values of C
    # 4 values of Ds
    # 1 value of Dc tested by every Ds value, 2 values from Dc tested by 3 of
    #  Ds, 3 values of Dc tested by 2 values of Ds and 4 values of dc tested
    # by 1 value of Ds
    # amount -> 3*3*4*(1*4+2*3+3*2+4*1)*iter
    print_search_space(ds_values, dc_values, c_values)
    initial_settings: list = []

    for c in c_values:
        for ds in ds_values:
            for dc in dc_values:
                if dc >= ds:
                    continue
                for size, size_name in map_sizes:
                    for _ in range(iteration_per_combination):
                        initial_settings.append((size, size_name, c, ds, dc))

    total = len(initial_settings)
    shuffle(initial_settings)
    count = 0
    t0 = time.process_time()
    t = 0
    eta = "--"
    for args in initial_settings:
        size, size_name, c, ds, dc = args

        pb.print_progress(count, total, prefix=f"Time estimated {eta}",
                          suffix=f"\t @ {round(t,3)}s/game\t curr ({size_name},"
                                 f"{c},{ds},{dc}) \tsim#{count}", bar_length=50)
        simulate_game(args, model_mode)
        count += 1
        t = (time.process_time() - t0) / count
        eta = estimate_time_before_arrival(t * (total - count))
