#!/usr/bin/env python3

import argparse
import subprocess
import codecs
import sys
from mpi4py import MPI

VERBOSE = False


def decode_utf8(string):
    return codecs.decode(string, 'UTF-8')


def run_server(cmd, dst, communicator):
    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    communicator.send('running', dest=dst)
    stdout, stderr = process.communicate()
    if stderr:
        print(f'Server error: {decode_utf8(stderr)}')
    if VERBOSE:
        print(f'Server output: {decode_utf8(stdout)}')


def run_client(cmd, source, communicator):
    sync = communicator.recv(source=source)
    process = subprocess.Popen(
        cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if stderr:
        print(f'Client error: {decode_utf8(stderr)}')
    if VERBOSE:
        print(f'Client received {sync}')
    print(decode_utf8(stdout))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Python wrapper script for network performance benchmarks')
    parser.add_argument('--servercmd', type=str, help='Server command e.g. --servercmd=[cmd].\
                         Iperf example: iperf -s -D -1.')
    parser.add_argument('--clientcmd', type=str,
                        help='Client command e.g. --clientcmd=[cmd]. Use HOSTNAME placeholder\
                        to indicate position of real hostname / address in benchmark string')
    parser.add_argument(
        '--verbose', action=argparse.BooleanOptionalAction, help='Enable debug output')
    args = parser.parse_args()

    if args.verbose:
        VERBOSE = True

    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    my_rank = comm.Get_rank()
    my_name = MPI.Get_processor_name()
    if size != 2:
        sys.exit()('Benchmark wrapper requires two processes!')

    OTHER_NAME = ''
    target_rank = (my_rank + 1) % size
    sreq = comm.isend(my_name, dest=target_rank)
    rreq = comm.irecv(source=target_rank)
    sreq.wait()
    OTHER_NAME = rreq.wait()

    if VERBOSE:
        print(f'rank {my_rank}: received hostname {OTHER_NAME}')

    if my_rank == 0:
        run_server(args.servercmd, target_rank, comm)
    else:
        clientcmd=args.clientcmd.replace('HOSTNAME', OTHER_NAME)
        if VERBOSE:
            print(f'clientcmd: {clientcmd}')
        run_client(clientcmd, target_rank, comm)
