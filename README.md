# Network Performance Benchmark Wrapper
## Dependancies
* python@3.10.8
* mpi4py
* os
* argparse
* codecs

## Basic Usage
Network performance benchmarks usually measure point-to-point connections, thus exactly two processes are required.
**HOSTNAME** is used as a wildcard parameter. It will be replaced by the real hostname running the server application during initialization.

### qperf
~~~
mpirun -n 2 ./npb_wrapper.py --servercmd="qperf" --clientcmd="qperf HOSTNAME [[PARAMETER]] quit"
~~~
**qperf** output does not leverage automated visualization. To address this problem one can pass a custom module to parse the output
in more suitable formats i.e. csv or json.
~~~
mpirun -n 2 ./npb_wrapper.py --servercmd="qperf" --clientcmd="qperf HOSTANME [[PARAMETER]] quit" --parser=qperf_parser.py --out_format=[[csv,json]] --header Metric Value Unit

### iperf
~~~
mpirun -n 2 ./npb_wrapper.py --servercmd="iperf3 -s -D -1 -f M"\
                             --clientcmd="iperf3 -c HOSTNAME -f M --json"
~~~

[![linting: pylint](https://img.shields.io/badge/linting-pylint-yellowgreen)](https://github.com/PyCQA/pylint)
