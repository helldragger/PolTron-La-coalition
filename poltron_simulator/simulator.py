from math import floor
from typing import Tuple


est_duration_secs = 60
est_cases_per_sec_per_player = 5
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
    if min_c == -1:
        min_c = 1
    if max_c == -1:
        area = m * n
        max_c = floor(area / est_cases_per_player) - 1

    return (min_c, max_c)


def parameterize_ds(min_ds: int, max_ds: int) -> Tuple[int, int]:
    # Un joueur lambda sur un jeu type tron armageddon peut se projeter
    # rapidement sur environ quelques secondes dans le futur
    # experimentalement avec beaucoup de joueurs (4), environ une à deux
    # secondes d'avance peuvent etre réfléchie en regardant le jeu de facon
    # globale sans détailler.
    # extrapolons et disons jusqu'à 10 secondes d'avance si on essaie de
    # prédire les décision d un autre joueur et d'un autre joueur uniquement

    # on va donc partir sur cette base et se dire qu'un joueur peut avoir une
    #  intelligence max de 2 secondes d'avance sur le jeu pour savoir où tout
    #  le monde se dirige
    if min_ds == -1:
        min_ds = 2

    if max_ds == -1:
        max_ds = est_cases_per_sec_per_player * 2

    return (min_ds, max_ds)


def parameterize_m(min_m: int, max_m: int) -> Tuple[int, int]:
    # des données arbitraires pour les tailles basiques de m
    if min_m == -1:
        min_m = 1
    if max_m == -1:
        max_m = 100
    return (min_m, max_m)


def parameterize_dc(max_ds: int, min_dc: int, max_dc: int) -> Tuple[int, int]:
    # sauf borné explicitement: 0 < dc < ds

    if min_dc == -1:
        min_dc = 1
    if max_dc == -1:
        max_dc = max_ds - 1

    return (min_dc, max_dc)


def parameterize_n(m: int, min_n: int, max_n: int) -> Tuple[int, int]:
    # pour avoir une aire suffisante pour accueillir des joueurs, il nous faut
    # que l equation pour C soit au moins supérieur à 1
    # cette equation est celle ci: maxC = ((MxN)/(cases_per_player))-1
    # soit (M*N/cases_per_player)-1 >= 1
    # -> M*N/cases_per_player >= 2
    # -> M*N >= 2*cases_per_player
    # -> N >= 2*cases_per_player/M
    if min_n == -1:
        min_n = 2 * est_cases_per_player / m
    if max_n == -1:
        max_n = 100
    return (min_n, max_n)


def simulate_game(m, n, c, ds, dc):
    import poltron_db.db as db
    game_id = db.get_last_game_id() + 1
    game = Game()
    game.run()

    db.insert_game_info(game_id, m, n, ds, dc, c)

    db.insert_game_result(game_id, game.last_tick, game.victory)

    for tick, deaths in game.deaths:
        db.insert_deaths(game_id, tick, deaths)

    for tick, nb_walls, c_deaths, map_string in game.important_moments:
        db.insert_important_moment(game_id, tick, nb_walls, c_deaths,
                                   map_string)

    for player_id, x, y in game.initial_positions:
        db.insert_initial_positions(game_id, player_id, x, y)

    for player_id, player_order in game.initial_order:
        db.insert_player_order(game_id, player_id, player_order)
    return


def generate_data(min_m: int = -1, min_n: int = -1, min_c: int = 1,
                  min_ds: int = -1, min_dc: int = -1, max_m: int = -1,
                  max_n: int = -1, max_c: int = -1, max_ds: int = -1,
                  max_dc: int = -1) -> None:
    min_m, max_m = parameterize_m(min_m, max_m)
    for m in range(min_m, max_m, 1):
        min_n, max_n = parameterize_n(m, min_n, max_n)
        for n in range(min_n, max_n, 1):
            min_c, max_c = parameterize_c(m, n, min_c, max_c)
            for c in range(min_c, max_c, 1):
                min_ds, max_ds = parameterize_ds(min_ds, max_ds)
                for ds in range(min_ds, max_ds, 1):
                    min_ds, max_ds = parameterize_dc(max_ds, min_dc, max_dc)
                    for dc in range(min_dc, max_dc, 1):
                        simulate_game(m, n, c, ds, dc)
