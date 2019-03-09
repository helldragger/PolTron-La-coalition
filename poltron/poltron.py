from argparse import ArgumentParser

import pyximport


pyximport.install(pyimport=True, load_py_module_on_import_failure=True)

from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

import poltron_db.db as db
import poltron_model.model as model
import poltron_simulator.simulator as sim
import poltron_util.progress_bar as pb
from poltron_game.Game import Game


def profiling(args):
    graphviz = GraphvizOutput()

    # if not args.model:
    #    for _ in range(10):
    #        cProfile.run('Game(10, 10, 4, 4, 3).run()')
    # else:
    #    for _ in range(10):
    #        cProfile.run('model.Model(10, 10, 4, 4, 3).run()')
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
                Game(10, 10, 4, 3, 2).run()
            else:
                model.Model(10, 10, 4, 3, 2).run()
            pb.print_progress(_ + 1, total, prefix=f"Profiling: ",
                              suffix=f"\tsim#{_+2}/{total}", bar_length=50)


def main(args):
    if args.profiler:
        profiling(args)
        return

    iteration_per_combination: int = args.iter

    model_mode: bool = args.model

    assert iteration_per_combination > 0, "Amount of iterations must be " \
                                          "positive"

    db.prepare_db_path(args)
    db.prepare_db_tables()

    sim.generate_data(iteration_per_combination, model_mode)


if __name__ == "__main__":
    parser = ArgumentParser()

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
