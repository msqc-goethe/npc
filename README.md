# Network Performance Benchmark Wrapper
## Dependancies
* python@3.10.8
* mpi4py
* os
* argparse
* codecs

## Basic Usage
Network performance benchmarks usually measure point-to-point connections, thus exactly two processes are required.

### iperf
~~~
mpirun -n 2 ./python-npb-wrapper --servercmd="iperf3 -s -D -1 -f M"\
                                 --clientcmd="iperf3 -c HOSTNAME -f M --json"
~~~
**HOSTNAME** is used as a wildcard parameter. It will be replaced by the real hostname running the server application during initialization.
[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
