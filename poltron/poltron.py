from argparse import ArgumentParser

import poltron_db.db as db
import poltron_simulator.simulator as sim


def main(args):
    db.prepare_db_tables()

    min_m: int = args.min_m
    min_n: int = args.min_n
    min_c: int = args.min_c
    min_ds: int = args.min_ds
    min_dc: int = args.min_dc
    max_m: int = args.max_m
    max_n: int = args.max_n
    max_c: int = args.max_c
    max_ds: int = args.max_ds
    max_dc: int = args.max_dc
    iteration_per_combination: int = args.iter
    m_step: int = args.step_m
    n_step: int = args.step_n
    c_step: int = args.step_c
    ds_step: int = args.step_ds
    dc_step: int = args.step_dc

    assert min_m > 0 and max_m > 0, "M must be positive"
    assert min_n > 0 and max_n > 0, "N must be positive"
    assert min_dc > 0 and max_dc > 0, "Dc must be positive"
    assert min_ds > 0 and max_ds > 0, "Ds must be positive"
    assert min_c > 0 and max_c > 0, "C must be positive"
    assert iteration_per_combination > 0, "Amount of iterations must be " \
                                          "positive"

    assert min_m <= max_m, "M minimum must be <= to its maximum"
    assert min_n <= max_n, "N minimum must be <= to its maximum"
    assert min_dc <= max_dc, "Dc minimum must be <= to its maximum"
    assert min_ds <= max_ds, "Ds minimum must be <= to its maximum"
    assert min_c <= max_c, "C minimum must be <= to its maximum"

    assert max_dc < max_ds and min_dc < min_ds, "Dc must be within 0<Dc<Ds"

    sim.generate_data(min_m, min_n, min_c, min_ds, min_dc, max_m, max_n, max_c,
        max_ds, max_dc, iteration_per_combination, m_step, n_step, c_step,
        ds_step, dc_step)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--min_m", action="store", default=10, type=int,
                        help="Sets the search space minimum value of m")
    parser.add_argument("--min_n", action="store", default=10, type=int,
                        help="Sets the search space minimum value of n")
    parser.add_argument("--min_c", action="store", default=1, type=int,
                        help="Sets the search space minimum value of c")
    parser.add_argument("--min_ds", action="store", default=10, type=int,
                        help="Sets the search space minimum value of ds")
    parser.add_argument("--min_dc", action="store", default=1, type=int,
                        help="Sets the search space minimum value of dc")
    parser.add_argument("--max_m", action="store", default=50, type=int,
                        help="Sets the search space maximum value of m")
    parser.add_argument("--max_n", action="store", default=50, type=int,
                        help="Sets the search space maximum value of n")
    parser.add_argument("--max_c", action="store", default=100, type=int,
                        help="Sets the search space maximum value of c")

    # Un joueur lambda sur un jeu type tron armageddon peut se projeter
    # rapidement sur environ quelques secondes dans le futur
    # experimentalement avec beaucoup de joueurs (4), environ une à deux
    # secondes d'avance peuvent etre réfléchie en regardant le jeu de facon
    # globale sans détailler.
    # extrapolons et disons jusqu'à 10 secondes d'avance si on essaie de
    # prédire les décision d un autre joueur et d'un autre joueur uniquement

    # on va donc partir sur cette base et se dire qu'un joueur peut avoir une
    #  intelligence max de 2 secondes d'avance sur le jeu pour savoir où tout
    #  le monde se dirige  -> max_ds = 10
    parser.add_argument("--max_ds", action="store", default=10, type=int,
                        help="Sets the search space maximum value of ds")
    parser.add_argument("--max_dc", action="store", default=9, type=int,
                        help="Sets the search space maximum value of dc")
    parser.add_argument("--step_m", action="store", default=10, type=int,
                        help="Sets the search space sampling interval of m")
    parser.add_argument("--step_n", action="store", default=10, type=int,
                        help="Sets the search space sampling interval of n")
    parser.add_argument("--step_c", action="store", default=5, type=int,
                        help="Sets the search space sampling interval of c")
    parser.add_argument("--step_ds", action="store", default=1, type=int,
                        help="Sets the search space sampling interval of ds")
    parser.add_argument("--step_dc", action="store", default=2, type=int,
                        help="Sets the search space sampling interval of dc")
    parser.add_argument("--iter", action="store", default=1000, type=int,
                        help="Sets the amount of random games simulated per "
                             "combination")

    main(parser.parse_args())
