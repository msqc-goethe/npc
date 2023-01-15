#!/usr/bin/env python3
import json


def to_format(input_string, header=None, out_format=None):
    """Convert iperf3 output string into one of the available formats i.e. csv or json"""
    if out_format == 'json':
        return json.loads(input_string)
