#!/usr/bin/env python3

import argparse
import codecs
import sys
import importlib
from subprocess import Popen, PIPE
from mpi4py import MPI


VERBOSE = False


class StreamParser:
    """Generic parser class encapsulating custom parser module"""
    def __init__(self, module, out_format, header_information):
        self.to_format = module.to_format
        self.format = out_format
        self.header = header_information

    def convert_to_format(self, string):
        """Get formated output"""
        return self.to_format(string, self.header, self.format)

    def get_format(self):
        """Get format"""
        return self.format

    def get_header(self):
        """Get header list"""
        return self.header


def decode_utf8(byte_code):
    """bytes -> string"""
    return codecs.decode(byte_code, 'UTF-8')


def run_server(cmd, dst, communicator):
    """Run server command. Notify client side when server is running."""
    with Popen(cmd.split(), stdout=PIPE, stderr=PIPE) as process:
        communicator.send('server msg', dest=dst)
        stdout, stderr = process.communicate()
        if stderr:
            print(f'Server error: {decode_utf8(stderr)}')
        if VERBOSE:
            print(f'Server output: {decode_utf8(stdout)}')


def run_client(cmd, source, communicator, stdout_parser=None):
    """Run client command."""
    sync = communicator.recv(source=source)
    with Popen(cmd.split(), stdout=PIPE, stderr=PIPE) as process:
        stdout, stderr = process.communicate()
        if stderr:
            print(f'Client error: {decode_utf8(stderr)}')
        if VERBOSE:
            print(f'Client received {sync}')
        stdout = decode_utf8(stdout)
        if stdout_parser:
            stdout = stdout_parser.convert_to_format(stdout)
        print(stdout)


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
    parser.add_argument('--parser', type=str, help='Use given parser to directly convert\
            benchmark output into desired format')
    parser.add_argument('--out_format', type=str,
                        help='Output format passed to custom cli parser')
    parser.add_argument('--header', nargs='+', type=str,
                        help='Header information')
    args = parser.parse_args()

    if args.verbose:
        VERBOSE = True

    if args.parser:
        if '.py' in args.parser:
            args.parser = args.parser.replace('.py', '')
        parser_module = importlib.import_module(args.parser)
        output_parser = StreamParser(
            parser_module, args.out_format, args.header)

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
        clientcmd = args.clientcmd.replace('HOSTNAME', OTHER_NAME)
        if VERBOSE:
            print(f'clientcmd: {clientcmd}')
        run_client(clientcmd, target_rank, comm,
                   output_parser if args.parser else None)
