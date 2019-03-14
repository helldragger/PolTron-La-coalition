# PolTron-La-coalition


```commandline
usage: poltron.py [-h] [--iter ITER] [--iterprofiler ITERPROFILER]
                  [--profiler] [--cProfile] [--graphProfile] [--model]
                  [--compiled]

optional arguments:
  -h, --help            show this help message and exit
  --iter ITER           Sets the amount of random games simulated per
                        combination
  --iterprofiler ITERPROFILER
                        Sets the amount of iterations for profiling.
  --profiler            Launch the profiler mode instead of the simulation
                        mode. Does nothing by itself, also choose among
                        available profiler tools to run it.
  --cProfile            Use cProfile profiler.
  --graphProfile        Use PyCallGraph profiler.
  --model               Launch the model based mode instead of the AI driven
                        mode
  --compiled            Use cython compilation and optimizations. (Needs to
                        have cython correctly installed)
```
