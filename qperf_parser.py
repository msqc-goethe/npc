#!/usr/bin/env python3


def to_format(input_string, header, out_format):
    """Convert qperf output string into one of the available formats i.e. csv or json"""
    lines = input_string.split('\n')
    name = lines.pop(0)
    end = 'quit:'
    output = [] if out_format == 'json' else header[0] + ',' + header[1] + ',' + header[2] + '\n'
    for line in lines:
        if end in line:
            break
        if name not in line:
            line = line.split()
            if len(line) > 3:
                unit = line[3]
            else:
                unit = 'NA'
            if out_format == 'json':
                output.append(
                    {header[0]: line[0], header[1]: line[2], header[2]: unit})
            elif out_format == 'csv':
                output += line[0] + ',' + line[2] + ',' + unit + '\n'
    return output
