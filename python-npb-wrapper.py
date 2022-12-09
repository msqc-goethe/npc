#!/usr/bin/env python3

import argparse
import subprocess
import codecs
from mpi4py import MPI

verbose = False

def decode_utf8(string):
    return codecs.decode(string,'UTF-8')

def run_server(servercmd,target_rank,comm):
    process = subprocess.Popen(servercmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    comm.send('running',dest = target_rank)
    stdout,stderr = process.communicate()
    if stderr:
        print('Server error: {err}'.format(err=decode_utf8(stderr)))
    if verbose:
        print('Server output: {out}'.format(out=decode_utf8(stdout)))
    return

def run_client(clientcmd,target_rank,comm):
    sync = comm.recv(source = target_rank)
    process = subprocess.Popen(clientcmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    stdout,stderr = process.communicate()
    if stderr:
        print('Client error: {err}'.format(err=decode_utf8(stderr)))
    if verbose:
        print('Client received {msg}'.format(msg=sync))
    print(decode_utf8(stdout))
    return

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python wrapper script for network performance benchmarks')
    parser.add_argument('--servercmd', type=str, help='Server command e.g. --servercmd=[cmd].\
                         Iperf example: iperf -s -D -1.')
    parser.add_argument('--clientcmd', type=str, help='Client command e.g. --clientcmd=[cmd]. Use HOSTNAME placeholder to indicate position of real hostname / address in benchmark string')
    parser.add_argument('--verbose', action=argparse.BooleanOptionalAction, help='Enable debug output')
    args = parser.parse_args()

    if args.verbose:
        verbose = True

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    my_rank = comm.Get_rank()
    my_name = MPI.Get_processor_name()
    if size != 2:
        quit('Benchmark wrapper requires two processes!')

    other_name = ''
    target_rank = (my_rank + 1) % size
    sreq = comm.isend(my_name, dest = target_rank)
    rreq = comm.irecv(source = target_rank)
    sreq.wait()
    other_name = rreq.wait()
    if verbose:
        print('rank {rank}: received hostname {name}'.format(rank=my_rank,name=other_name))

    if my_rank == 0:
        run_server(args.servercmd,target_rank,comm)
    else:
        clientcmd = args.clientcmd.replace('HOSTNAME',other_name)
        if verbose:
            print('clientcmd: {cmd}'.format(cmd = clientcmd))
        run_client(clientcmd,target_rank,comm)
