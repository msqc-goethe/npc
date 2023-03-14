# Network Performance Collector

## Workflow Implementation

## Dependencies
* python@3.2
* [JUBE](https://apps.fz-juelich.de/jsc/jube/jube2/docu/index.html)

## Basic Usage
```
jube run workflow/roofline-workflow.yaml
jube continue [[WORKING DIRECTORY]]
jube analyse [[WORKING DIRECTORY]]
jube result [[WORKKING DIRECOTRY]]
./rooline.R
```
## Network Performance Benchmark Script

### Dependencies
* python@3.10.8
* mpi4py
* os
* argparse
* codecs

### Basic Usage
Network performance benchmarks usually measure point-to-point connections, thus exactly two processes are required.
**HOSTNAME** is used as a wildcard parameter. It will be replaced by the real hostname running the server application during initialization.

#### qperf
~~~
mpirun -n 2 ./npb.py --servercmd="qperf" --clientcmd="qperf HOSTNAME [[PARAMETER]] quit"
~~~
