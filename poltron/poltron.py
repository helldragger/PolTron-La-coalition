from argparse import ArgumentParser

# pyximport.install(pyimport=True, load_py_module_on_import_failure=True)
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

import poltron_db.db as db
import poltron_model.model as model
import poltron_simulator.simulator as sim
import poltron_util.progress_bar as pb
from poltron_game.Game import Game


# import pyximport;

def profiling(args):
    graphviz = GraphvizOutput()

    # if not args.model:
    #    for _ in range(10):
    #        cProfile.run('Game.Game(30, 50, 20, 10, 5).run()')
    # else:
    #    for _ in range(10):
    #        cProfile.run('model.Model(30, 50, 20, 10, 5).run()')
    total = 10

    if not args.model:
        graphviz.output_file = 'game_profile_graph.png'
    else:
        graphviz.output_file = 'model_profile_graph.png'
    with PyCallGraph(output=graphviz):

        pb.print_progress(0, total, prefix=f"Profiling: ",
                          suffix=f"\tsim#1/{total}", bar_length=50)
        for _ in range(total):



            if not args.model:
                Game(10, 10, 5, 2, 1).run()
            else:
                model.Model(50, 50, 20, 10, 5).run()
            pb.print_progress(_ + 1, total, prefix=f"Profiling: ",
                              suffix=f"\tsim#{_+2}/{total}", bar_length=50)


def main(args):
    if args.profiler:
        profiling(args)
        return


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

    model_mode: bool = args.model

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
    db.prepare_db_path(args)
    db.prepare_db_tables()

    sim.generate_data(min_m, min_n, min_c, min_ds, min_dc, max_m, max_n, max_c,
                      max_ds, max_dc, iteration_per_combination, m_step, n_step, c_step,
                      ds_step, dc_step, model_mode)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--min_m", action="store", default=5, type=int,
                        help="Sets the search space minimum value of m")
    parser.add_argument("--min_n", action="store", default=5, type=int,
                        help="Sets the search space minimum value of n")
    parser.add_argument("--min_c", action="store", default=1, type=int,
                        help="Sets the search space minimum value of c")
    parser.add_argument("--min_ds", action="store", default=2, type=int,
                        help="Sets the search space minimum value of ds")
    parser.add_argument("--min_dc", action="store", default=1, type=int,
                        help="Sets the search space minimum value of dc")

    parser.add_argument("--max_m", action="store", default=50, type=int,
                        help="Sets the search space maximum value of m")
    parser.add_argument("--max_n", action="store", default=50, type=int,
                        help="Sets the search space maximum value of n")
    parser.add_argument("--max_c", action="store", default=100, type=int,
                        help="Sets the search space maximum value of c")
    parser.add_argument("--max_ds", action="store", default=10, type=int,
                        help="Sets the search space maximum value of ds")
    parser.add_argument("--max_dc", action="store", default=9, type=int,
                        help="Sets the search space maximum value of dc")

    parser.add_argument("--step_m", action="store", default=5, type=int,
                        help="Sets the search space sampling interval of m")
    parser.add_argument("--step_n", action="store", default=5, type=int,
                        help="Sets the search space sampling interval of n")
    parser.add_argument("--step_c", action="store", default=5, type=int,
                        help="Sets the search space sampling interval of c")
    parser.add_argument("--step_ds", action="store", default=2, type=int,
                        help="Sets the search space sampling interval of ds")
    parser.add_argument("--step_dc", action="store", default=2, type=int,
                        help="Sets the search space sampling interval of dc")

    parser.add_argument("--iter", action="store", default=100, type=int,
                        help="Sets the amount of random games simulated per "
                             "combination")

    parser.add_argument("--profiler", action="store_true",
                        help="Launch the profiler mode instead of the "
                             "simulation mode")
    parser.add_argument("--model", action="store_true",
                        help="Launch the model based mode instead of the "
                             "AI driven mode")

    main(parser.parse_args())
