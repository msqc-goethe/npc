#!/usr/bin/env python3

import argparse
import codecs
import sys
import re
from subprocess import Popen, PIPE
from mpi4py import MPI


VERBOSE = False


def decode_utf8(byte_code):
    """bytes -> string"""
    return codecs.decode(byte_code, 'UTF-8')


def run_server(cmd, dst, communicator, kill_server=False):
    """Run server command. Notify client side when server is running."""
    with Popen(cmd.split(), stdout=PIPE, stderr=PIPE) as process:
        communicator.send('server msg', dest=dst)
        if kill_server:
            sync = communicator.recv(source=dst)
            if VERBOSE:
                print(f'Server received {sync}')
            process.terminate()
            stdout, stderr = process.communicate()
        else:
            stdout, stderr = process.communicate()
        if stderr:
            print(f'Server error: {decode_utf8(stderr)}')
            communicator.Abort()
        if VERBOSE:
            print(f'Server output: {decode_utf8(stdout)}')


def run_client(cmd, source, communicator):
    """Run client command."""
    if not run_client.already_synced:
        sync = communicator.recv(source=source)
        if VERBOSE:
            print(f'Client received {sync}')
        run_client.already_synced = True
    with Popen(cmd.split(), stdout=PIPE, stderr=PIPE) as process:
        stdout, stderr = process.communicate()
        if stderr:
            print(f'Client error: {decode_utf8(stderr)}')
        return decode_utf8(stdout)


def evaluate_repeat_regex(string):
    """Check input string for repeat keyword and arguments"""
    repeat_regex = '-{1,2}repeat\s(([a-z]|[_,-])+):([0-9])+:([0-9])+:([\-,\+,\*,\/])([0-9])+'
    repeat_string = re.search(repeat_regex, string)
    if repeat_string:
        tmp_string = repeat_string.group(0).split()
        config = tmp_string[1].split(':')
        cmd = config[0]
        begin = config[1]
        end = config[2]
        operator_and_step = config[3]
        operator = operator_and_step[0]
        step = operator_and_step[1:]
        if VERBOSE:
            print(f'Repeat: {cmd} {begin} {end} {operator} {step}')
        string = re.sub(repeat_regex, 'REPEAT', string, 1)
        return [string, cmd, begin, end, operator, step]
    return []


def run_repeated_client_cmd(cmdstring, dst, communicator):
    """Loop through parametes and perform actual measurement"""
    run_client.already_synced = False
    repeat_list = evaluate_repeat_regex(cmdstring)
    cmdstring = repeat_list[0]
    cmd = repeat_list[1]
    begin = int(repeat_list[2])
    end = int(repeat_list[3])
    operator = repeat_list[4]
    step = int(repeat_list[5])
    i = begin

    while i <= end:
        if '--REPEAT':
            repeat_cmd = '--' + cmd + ' ' + str(i)
        else:
            repeat_cmd = '-' + cmd + ' ' + str(i)
        run_cmd = cmdstring.replace('REPEAT', repeat_cmd)

        if VERBOSE:
            print(f'client_cmd: {run_cmd}')

        res = run_client(run_cmd, dst, communicator)
        if operator == '+':
            i += step
        elif operator == '*':
            i *= step
        else:
            print('Error computing step size')
            communicator.Abort()
        print(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Python wrapper script for network performance benchmarks')
    parser.add_argument('--servercmd', type=str, help='Server command e.g. --servercmd=[cmd].\
                         Iperf example: iperf -s -D -1.')
    parser.add_argument('--clientcmd', type=str,
                        help='Client command e.g. --client_cmd=[cmd]. Use HOSTNAME placeholder\
                        to indicate position of real hostname / address in benchmark string')
    parser.add_argument(
        '--killserver', action=argparse.BooleanOptionalAction, help='Terminator server\
                        side after measurements.')
    parser.add_argument(
        '--verbose', action=argparse.BooleanOptionalAction, help='Enable debug output')
    parser.add_argument('--modify_hostname',nargs='+',type=str,
                        help='Replaces given part of the of the hostname\
                        --modify_hostname [SEARCH FOR] [REPLACE BY]')
    args = parser.parse_args()
    KILL = False
    if args.verbose:
        VERBOSE = True
    if args.killserver:
        KILL = True

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
        server_cmd = args.servercmd
        if args.modify_hostname:
            my_name = my_name.replace(args.modify_hostname[0],args.modify_hostname[1])
            server_cmd = args.servercmd.replace('HOSTNAME',my_name)
        run_server(server_cmd, target_rank, comm, kill_server=KILL)
    else:
        if args.modify_hostname:
            OTHER_NAME = OTHER_NAME.replace(args.modify_hostname[0],args.modify_hostname[1])
            if VERBOSE:
                print(f'Modified hostname is now {OTHER_NAME}')
        client_cmd = args.clientcmd.replace('HOSTNAME', OTHER_NAME)
        if '-repeat' in client_cmd:
            run_repeated_client_cmd(
                client_cmd, target_rank, comm)
        else:
            run_client.already_synced = False
            res = run_client(client_cmd, target_rank, comm)
            print(res)
        if KILL:
            comm.send('kill server msg', dest=0)
