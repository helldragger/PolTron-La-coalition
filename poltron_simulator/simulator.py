# -*- coding: utf-8 -*-
from math import floor
from random import shuffle
from typing import Tuple

import poltron_util.progress_bar as pb
from poltron_game.Game import Game
from poltron_model import model


est_duration_secs = 60
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


def parameterize_n(m: int, min_n: int, max_n: int) -> Tuple[int, int]:
    # pour avoir une aire suffisante pour accueillir des joueurs, il nous faut
    # que l equation pour C soit au moins supérieur à 1
    # cette equation est celle ci: maxC = ((MxN)/(cases_per_player))-1
    # soit (M*N/cases_per_player)-1 >= 1
    # -> M*N/cases_per_player >= 2
    # -> M*N >= 2*cases_per_player
    # -> N >= 2*cases_per_player/M
    min_n = max(int(2 * est_cases_per_player / m), min_n)
    return min_n, max_n


def simulate_game(args, model_mode):
    import poltron_db.db as db
    m, n, c, ds, dc = args
    game_id = db.get_last_game_id() + 1
    if model_mode:
        game = model.Model(m, n, c, ds, dc)
        game.run()
    else:
        game = Game(m, n, c, ds, dc)
        game.run()

    db.insert_game_info(game_id, m, n, ds, dc, c)

    db.insert_game_result(game_id, game.tick, game.victory)

    for tick, deaths in game.deaths:
        db.insert_deaths(game_id, tick, deaths)

    for tick, nb_walls, c_deaths in game.important_moments:
        db.insert_important_moment(game_id, tick, nb_walls, c_deaths)

    for player_id, x, y in game.initial_positions:
        db.insert_initial_positions(game_id, player_id, x, y)

    for player_id, player_order in game.initial_order:
        db.insert_player_order(game_id, player_id, player_order)
    return


def print_search_space(sp: Tuple[int, int, int, int, int, int], m_step, n_step,
                       c_step, ds_step, dc_step) -> None:
    count, highest_m, highest_n, highest_c, highest_ds, highest_dc = sp
    print(f"Total amount of simulations to do: {count}")
    print(f"highest map M size: {highest_m} \t\t\t sampled every {m_step}")
    print(f"highest map N size: {highest_n} \t\t\t sampled every {n_step}")
    print(f"highest Coalition size: {highest_c} \t\t sampled every {c_step}")
    print(f"highest solo research level: {highest_ds}\t\t sampled every "
          f"{ds_step}")
    print(f"highest coalition research level: {highest_dc}\t sampled every "
          f"{dc_step}")
    print("\n")


def estimate_time_before_arrival(secs: int):
    mins = max(0, secs // 60)
    hours = max(0, mins // 60)
    days = max(0, hours // 24)

    hours %= 24
    mins %= 60
    secs %= 60

    return f"{int(days)}d {int(hours)}h {int(mins)}m {int(secs)}s"


def calculate_simulation_amount(min_m: int, min_n: int, min_c: int, min_ds: int,
                                min_dc: int, max_m: int, max_n: int, max_c: int,
                                max_ds: int, max_dc: int,
                                iteration_per_combination: int, m_step, n_step,
                                c_step, ds_step, dc_step) -> Tuple[
    int, int, int, int, int, int]:

    _min_m, _max_m = (min_m, max_m)
    _min_ds, _max_ds = (min_ds, max_ds)
    count = 0
    highest_c = 0
    highest_n = 0
    highest_dc = 0
    highest_ds = _max_ds
    highest_m = _max_m
    for m in range(_min_m, _max_m + 1, m_step):
        _min_n, _max_n = parameterize_n(m, min_n, max_n)
        highest_n = max(highest_n, _max_n)
        for n in range(_min_n, _max_n + 1, n_step):
            _min_c, _max_c = parameterize_c(m, n, min_c, max_c)
            highest_c = max(highest_c, _max_c)
            for c in range(_min_c, _max_c + 1, c_step):
                for ds in range(_min_ds, _max_ds + 1, ds_step):
                    _min_dc, _max_dc = (min_dc, min(ds - 1, max_dc))
                    highest_dc = max(highest_dc, _max_dc)
                    for dc in range(_min_dc, _max_dc + 1, dc_step):
                        count += iteration_per_combination

    return count, highest_m, highest_n, highest_c, highest_ds, highest_dc


def generate_data(min_m: int, min_n: int, min_c: int, min_ds: int, min_dc: int,
                  max_m: int, max_n: int, max_c: int, max_ds: int, max_dc: int,
                  iteration_per_combination: int, m_step: int, n_step: int,
                  c_step: int, ds_step: int, dc_step: int,
                  model_mode: bool) -> None:
    import time

    search_space = calculate_simulation_amount(min_m, min_n, min_c, min_ds,
                                               min_dc, max_m, max_n, max_c,
                                               max_ds, max_dc,
                                               iteration_per_combination,
                                               m_step, n_step, c_step, ds_step,
                                               dc_step)
    print_search_space(search_space, m_step, n_step, c_step, ds_step, dc_step)
    _min_m, _max_m = (min_m, max_m)
    _min_ds, _max_ds = (min_ds, max_ds)
    initial_settings: list = []
    for m in range(_min_m, _max_m + 1, m_step):
        _min_n, _max_n = parameterize_n(m, min_n, max_n)
        for n in range(_min_n, _max_n + 1, n_step):
            _min_c, _max_c = parameterize_c(m, n, min_c, max_c)
            for c in range(_min_c, _max_c + 1, c_step):
                for ds in range(_min_ds, _max_ds + 1, ds_step):
                    _min_dc, _max_dc = (min_dc, min(ds - 1, max_dc))
                    for dc in range(_min_dc, _max_dc + 1, dc_step):
                        for _ in range(iteration_per_combination):
                            initial_settings.append((m, n, c, ds, dc))

    total = len(initial_settings)
    shuffle(initial_settings)
    count = 0
    t0 = time.process_time()
    for args in initial_settings:
        m, n, c, ds, dc = args
        simulate_game(args, model_mode)
        count += 1
        t = (time.process_time() - t0) / count
        eta = estimate_time_before_arrival(t * (total - count))
        pb.print_progress(count, total, prefix=f"Time estimated {eta}",
                          suffix=f"\t @ {round(t,3)}s/game\t curr ({m},{n},"
                                 f"{c},{ds},{dc}) \tsim#{count}", bar_length=50)
